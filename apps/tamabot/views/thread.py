import os
from apps.common.views import AppAPIView,NonAuthenticatedAPIMixin,AppModelListAPIViewSet
from apps.tamabot.config import ChatbotTypeChoices
from apps.tamabot.models import Thread,Message 
from apps.tamabot.serializers import TamaResponseSerializer,MessageSerializer,ThreadListSerializer
from apps.tamabot.serializers.thread import ThreadCreateSerializer
from apps.tamabot.views.emotional_chatbot import MentalHealthSupportTool, emotional_chatbot_prompt
from apps.tamabot.views.support_chatbot import support_chatbot_prompt
from .system_messagev2 import love_hope_system_template_V2
from .system_message import love_hope_system_template
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from django.http import StreamingHttpResponse
from typing import Optional,Literal, List
from pydantic import BaseModel, Field
import requests
from django.conf import settings
import json
from django_filters import rest_framework as filters
from apps.common.helpers import log_to_cloudwatch
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

book_couch_link = settings.BOOK_COUCH_LINK
therapist_url = settings.THERAPIST_URL

DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_DB")
connection = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)
vector_store = PGVector(
    embeddings=embedding_model,
    collection_name="docs",
    connection=connection,
    use_jsonb=True,
)

class ThreadFilter(filters.FilterSet):
    categories = filters.CharFilter(method='filter_categories')
    class Meta:
        model = Thread
        fields = {
            'created': ['date__gte', 'date__lte'],
            'uuid': ['exact'],
        }

    def filter_categories(self, queryset, name, value):
        """
        Filter threads where the categories field contains the given value.
        """
        if value:
            return queryset.filter(categories__contains=[value])
        return queryset


class MentalHealthSupport(BaseModel):
    """Schema for selecting professional mental health support options for Booking."""

    councelling_for: Optional[Literal["individual_counselling", "child_counselling", "partner_counselling","family_counselling"]] = Field(
        default="individual_counselling",  # default to "feature_a"
        description="Determines the type of councelling  for the user"
    )
    
    level_of_experience: Optional[Literal[ "basic","advance","expert"]]=Field(
          default="basic", description="Expectation of therapist level of experience by the user"
    )
    reasons:Optional[List[Literal[ "Trauma/PTSD","Mental Illness","Grief and Loss","Anxiety","Relationship Issues","Depression","Family Concerns",
    "Self-Esteem","Anger Management","Substance Abuse","Eating Disorders","LGBTQ+ Related Concerns","Body Image Issues","Parenting Challenges","Phobias",
    "Postpartum Depression","Burnout","Coping with Medical Conditions","Coping with Disability","General Stress"]]]=Field(
    default=None, description="fetch Only the Reasons given above  which aligns to the user's problems as much as possible"
    )

class NewThreadAPIView(NonAuthenticatedAPIMixin,AppAPIView):
    """API View to create New thread for chat"""
    def post(self, request, *args, **kwargs):
        """Handle get request to create a new thread"""
        try:
            serializer = ThreadCreateSerializer(data=request.data)
            if serializer.is_valid():
                chatbot_type = serializer.validated_data["chatbot_type"]
                thread = Thread.objects.create(chatbot_type=chatbot_type)
                if chatbot_type == ChatbotTypeChoices.emotional:
                    ai_response = "Absolutely! I’m here to listen.What’s on your mind? Feel free to share anything you’re comfortable with."
                    Message.objects.create(
                        thread=thread,
                        user_question="Hey hi",
                        ai_answer=ai_response,
                    )
                elif chatbot_type == ChatbotTypeChoices.support:
                    ai_response = "Great choice! We have a variety of services to support your mental wellness. Which one would you like to learn more about?\n1.Book A Couch (Counseling)\n2.Love Hope Circles (Support Groups)\n3.EITA (For Kids and Parents)\n4.Wellness At Work (For Organizations)\n5.Others."
                    Message.objects.create(
                        thread=thread,
                        user_question="Hey hi",
                        ai_answer=ai_response,
                    )
                return self.send_response({"thread_id": str(thread.uuid)})
            return self.send_error_response(serializer.errors)
        except Exception as e:
            return self.send_error_response({"message": "Error creating thread", "error":str(e)})

    
    

class ListThreadsViewSet(NonAuthenticatedAPIMixin,AppModelListAPIViewSet):

    queryset = Thread.objects.filter(messages__isnull=False).distinct().order_by("-created")
    serializer_class = ThreadListSerializer
    filterset_class = ThreadFilter
    search_fields = ["uuid"]
    all_table_columns = {
        "uuid": "Conversation ID",
        "categories": "Category",
        "is_book_couch": "Book a couch",
        "created": "Start Date",
        "last_conversation": "End Date",
    }

    def get_meta_for_table(self) -> dict:
        data = {
            "columns": self.get_table_columns()
        }
        return data


class MessageListAPIViewSet(NonAuthenticatedAPIMixin,AppModelListAPIViewSet):
    """API to list all Branch"""
    queryset=Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        
        thread_id = self.request.query_params.get('thread_id')
        reverse_order = self.request.query_params.get('reverse', 'false').lower() == 'true'

        if thread_id:
            q = super().get_queryset().filter(thread__uuid=thread_id)
            if reverse_order:
                return q.order_by('-created')  
            return q
        return Message.objects.none() 
    
# This Is Sychronous Code
    
# class TamaStreamingResponseAPIView(NonAuthenticatedAPIMixin,AppAPIView):

#     def gen_ai(self,formatted_messages,user_question,thread):
#         try:
#             system_template=love_hope_system_template_V2
#             prompt_template = ChatPromptTemplate.from_messages([
#             ('system', system_template),
#             *formatted_messages,
#             ('user', '{text}')
#                 ])
#             yield f"data: {json.dumps({'type': 'status', 'content': 'started'})}\n\n"
#             model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2,max_tokens=300)
#             parser = StrOutputParser()
#             chain = prompt_template | model | parser
#             ai_answer_chunks = []
#             for chunk in chain.stream({"text": user_question }):
#                 ai_answer_chunks.append(chunk)
#                 yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
                
            
#             ai_response = "".join(ai_answer_chunks)
#             message_obj=Message.objects.create(
#                     thread=thread,
#                     user_question=user_question,
#                     ai_answer=ai_response,
#                     )
#             yield f"data: {json.dumps({'type': 'status', 'content': 'completed'})}\n\n"
#             if book_couch_link in ai_response:
#                 yield f"data: {json.dumps({'type': 'fetching_service', 'content': 'fetching'})}\n\n"
#                 thread.is_book_couch = True
#                 llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)
#                 structured_llm = llm.with_structured_output(MentalHealthSupport)
#                 new_question = ('user',user_question)
#                 formatted_messages.append(new_question)
#                 a=structured_llm.invoke(f'{formatted_messages}')
#                 url = therapist_url
#                 headers = {
#                     "Content-Type": "application/json"
#                 }
#                 if a.reasons:
#                     thread.add_categories_to_thread(thread,a.reasons)
#                     reasons_param = ','.join(a.reasons)
#                 else:
#                     reasons_param = None
#                 params = {
#                     "counselling_type": a.councelling_for,    
#                     "level_of_experience": a.level_of_experience, 
#                     "reasons": reasons_param,                         
#                 }
#                 response = requests.get(url, headers=headers, params=params)
#                 if response.status_code==200:
#                     data = response.json()
#                     therapist_data = data.get('data', {}).get('results', [])
#                     yield f"data: {json.dumps({'type': 'therapist_details', 'content': therapist_data})}\n\n"
#                     message_obj.therapist = therapist_data
#                     message_obj.save()
#             thread.last_conversation = message_obj.created
#             thread.save()
#             yield f"data: {json.dumps({'type': 'status', 'content': 'finished'})}\n\n"
#         except Exception as e:
#                 error_message = f"Error occurred: {str(e)}"
#                 print(error_message)
#                 # log_to_cloudwatch(error_message=error_message)

#     def post(self, request, *args, **kwargs):
#         """Handle POST request to for Tama answers """
#         serializer = TamaResponseSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 user_question = serializer.validated_data['user_question']
#                 thread_id = serializer.validated_data['thread_id']
#                 try:
#                     thread = Thread.objects.get(uuid=thread_id)
#                 except Thread.DoesNotExist:
#                     return self.send_error_response({"error": "Invalid thread ID"})    
#                 messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
#                 messages = messages[::-1]
#                 formatted_messages = []
#                 for msg in messages:
#                     formatted_messages.append(("user", msg['user_question']))
#                     formatted_messages.append(("assistant", msg['ai_answer']))
#                 response = StreamingHttpResponse(self.gen_ai(formatted_messages,user_question,thread), content_type='text/event-stream')
#                 response['Cache-Control'] = 'no-cache'  
#                 response["X-Accel-Buffering"] = "no" 
#                 return response
#             except Exception as e:
#                 error_message = f"Error occurred: {str(e)}"
#                 print(error_message)
#                 # log_to_cloudwatch(error_message=error_message)
#         return self.send_error_response({"message":serializer.errors})





from adrf.views import APIView
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework import status
import httpx


class TamaStreamingResponseAPIView(NonAuthenticatedAPIMixin,APIView):

    async def gen_ai(self,formatted_messages,user_question,thread):    
        system_template=love_hope_system_template_V2
        prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        *formatted_messages,
        ('user', '{text}')
            ])
        is_book_couch=thread.is_book_couch
        reasons_list=[]
        therapist_data=[]
        yield  f"data: {json.dumps({'type': 'status', 'content': 'started'})}\n\n"
        try:    
            model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2,max_tokens=300)
            parser = StrOutputParser()
            chain = prompt_template | model | parser
            ai_answer_chunks = []
            async for chunk in chain.astream({"text": user_question }):
                ai_answer_chunks.append(chunk)
                yield  f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
            ai_response = "".join(ai_answer_chunks)
        except Exception as e:
            ai_response = "Tama is in High Demand, Please Try Again in Few Minutes"
            yield  f"data: {json.dumps({'type': 'message_delta', 'content': ai_response})}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'content': 'completed'})}\n\n"

        if book_couch_link in ai_response:
            yield f"data: {json.dumps({'type': 'fetching_service', 'content': 'fetching'})}\n\n"
            is_book_couch = True
            try:
                llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)
                structured_llm = llm.with_structured_output(MentalHealthSupport)
                new_question = ('user',user_question)
                formatted_messages.append(new_question)
                a=await structured_llm.ainvoke(f'{formatted_messages}')
                url = therapist_url
                headers = {
                    "Content-Type": "application/json"
                }
                if a.reasons:
                    reasons_list = a.reasons
                    reasons_param = ','.join(a.reasons)
                else:
                    reasons_param = None
                params = {
                    "counselling_type": a.councelling_for,    
                    "level_of_experience": a.level_of_experience, 
                    "reasons": reasons_param,                         
                }
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    therapist_data = data.get('data', {}).get('results', [])
                    yield f"data: {json.dumps({'type': 'therapist_details', 'content': therapist_data})}\n\n"
            except:
                yield f"data: {json.dumps({'type': 'therapist_details', 'content': therapist_data})}\n\n"
        message_obj = await sync_to_async(Message.objects.create)(
        thread=thread,
        user_question=user_question,
        ai_answer=ai_response,
        therapist=therapist_data
        )
        thread.is_book_couch = is_book_couch
        thread.last_conversation = message_obj.created
        if reasons_list:
        # Add categories to the thread asynchronously
            await sync_to_async(thread.add_categories_to_thread)(thread, reasons_list)
        else:
        # Save the thread asynchronously
            await sync_to_async(thread.save)()

        yield f"data: {json.dumps({'type': 'status', 'content': 'finished'})}\n\n"


    def get_thread_messages(self,thread):
        messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
        messages = messages[::-1]
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(("user", msg['user_question']))
            formatted_messages.append(("assistant", msg['ai_answer']))
        return formatted_messages  

    async def post(self, request, *args, **kwargs):
        """Handle POST request to for Tama answers """
        serializer = TamaResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:        
                user_question = serializer.validated_data['user_question']
                thread_id = serializer.validated_data['thread_id']
                try:
                    thread = await sync_to_async(Thread.objects.get)(uuid=thread_id)
                except Thread.DoesNotExist:
                    return Response({"message": f"Thread:{thread_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
                messages = await sync_to_async(self.get_thread_messages)(thread)
                response = StreamingHttpResponse(self.gen_ai(messages,user_question,thread), content_type='text/event-stream')
                response['Cache-Control'] = 'no-cache'  
                response["X-Accel-Buffering"] = "no" 
                return response
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
                return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return  Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class TamaChatbotStreamingResponseAPIView(NonAuthenticatedAPIMixin, APIView):

    async def emotional_gen_ai(self, formatted_messages, user_question, thread):    
        system_template = emotional_chatbot_prompt()
        prompt_template = ChatPromptTemplate.from_messages([
            ('system', system_template),
            *formatted_messages,
            ('user', '{text}')
        ])

        is_book_couch = thread.is_book_couch
        reasons_list=[]
        tool_call_args = ""
        tool_name = tool_id = ""
        yield f"data: {json.dumps({'type': 'status', 'content': 'started'})}\n\n"

        try:
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=300)
            model_with_tools = model.bind_tools(tools=[MentalHealthSupportTool])
            parser = StrOutputParser()
            chain = prompt_template | model_with_tools

            ai_answer_chunks = []
            tool_call_detected = False
            tool_response=""

            async for chunk in chain.astream(user_question):
                if chunk.tool_call_chunks:
                    tool_call_detected = True
                    for tool_call in chunk.tool_call_chunks:
                        tool_name = tool_call.get("name", "")
                        tool_id = tool_call.get("id", "")
                        tool_call_args += tool_call.get("args", "")
                elif chunk.content:
                    ai_answer_chunks.append(chunk.content)
                    yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk.content})}\n\n"

            if tool_call_detected and tool_call_args:
               
                tool_call = {
                    "name": tool_name,
                    "id": tool_id,
                    "args": json.loads(tool_call_args),
                }

                params = {
                    k: ",".join(f'{item}' for item in v) if isinstance(v, list) else v
                    for k, v in tool_call["args"].items()
                }
                reasons_list = json.loads(tool_call_args).get("reasons", [])
            
                # Call your therapist API
                headers = {
                    "Content-Type": "application/json"
                }

                async with httpx.AsyncClient() as client:
                    response = await client.get(therapist_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    is_book_couch=True
                
                    tool_response = data.get('data', {}).get('results', [])

                    prompt_template = ChatPromptTemplate.from_messages([
                        ("system", system_template),
                        *formatted_messages,
                        ("ai", "Here are the therapist booking links"),
                        ("user", "{text}")
                    ])

                    chain = prompt_template | model | parser
                    ai_answer_chunks = []

                    async for chunk in chain.astream({
                        "text": user_question,
                        "tool_response": json.dumps(tool_response)
                    }):
                        ai_answer_chunks.append(chunk)
                        yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
                    yield f"data: {json.dumps({'type': 'tool_calling', 'tool_response': tool_response})}\n\n"
                    # print(tool_response)
            ai_response = "".join(ai_answer_chunks)
        except Exception as e:
            print(e)
            ai_response = "Tama is in High Demand, Please Try Again in Few Minutes"
            yield f"data: {json.dumps({'type': 'message_delta', 'content': ai_response})}\n\n"

        yield f"data: {json.dumps({'type': 'status', 'content': 'completed'})}\n\n"
        # print(ai_response)
        message_obj = await sync_to_async(Message.objects.create)(
        thread=thread,
        user_question=user_question,
        ai_answer=ai_response,
        therapist=tool_response
        )
        thread.is_book_couch = is_book_couch
        thread.last_conversation = message_obj.created
        if reasons_list:
        # Add categories to the thread asynchronously
            await sync_to_async(thread.add_categories_to_thread)(thread, reasons_list)
        else:
        # Save the thread asynchronously
            await sync_to_async(thread.save)()

        yield f"data: {json.dumps({'type': 'status', 'content': 'finished'})}\n\n"

    async def support_gen_ai(self, formatted_messages, user_question, thread, doc):
        system_template = support_chatbot_prompt(doc)
        prompt_template = ChatPromptTemplate.from_messages([
            ('system',system_template+" {context}"),
            *formatted_messages,
            ('user', '{text}')
        ])

        is_book_couch = thread.is_book_couch
        reasons_list=[]
        tool_call_args = ""
        tool_name = tool_id = ""
        yield f"data: {json.dumps({'type': 'status', 'content': 'started'})}\n\n"

        try:
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=300)
            model_with_tools = model.bind_tools(tools=[MentalHealthSupportTool])
            parser = StrOutputParser()
            chain = prompt_template | model_with_tools

            ai_answer_chunks = []
            tool_call_detected = False
            tool_response=""

            async for chunk in chain.astream({
                        "text": user_question,
                        "context": doc
                    }):
                if chunk.tool_call_chunks:
                    tool_call_detected = True
                    for tool_call in chunk.tool_call_chunks:
                        tool_name = tool_call.get("name", "")
                        tool_id = tool_call.get("id", "")
                        tool_call_args += tool_call.get("args", "")
                elif chunk.content:
                    ai_answer_chunks.append(chunk.content)
                    yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk.content})}\n\n"

            if tool_call_detected and tool_call_args:
                # print(tool_call_args)
                tool_call = {
                    "name": tool_name,
                    "id": tool_id,
                    "args": json.loads(tool_call_args),
                }
                params = {
                    k: ",".join(f'{item}' for item in v) if isinstance(v, list) else v
                    for k, v in tool_call["args"].items()
                }

                reasons_list = json.loads(tool_call_args).get("reasons", [])
            
                # Call your therapist API
                headers = {
                    "Content-Type": "application/json"
                }

                async with httpx.AsyncClient() as client:
                    response = await client.get(therapist_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    is_book_couch=True
                
                    tool_response = data.get('data', {}).get('results', [])

                    prompt_template = ChatPromptTemplate.from_messages([
                        ("system", system_template+ "{context}"),
                        *formatted_messages,
                        ("ai", "Here are the therapist booking links"),
                        ("user", "{text}")
                    ])

                    chain = prompt_template | model | parser
                    ai_answer_chunks = []

                    async for chunk in chain.astream({
                        "text": user_question,
                        "context": doc
                    }):
                        ai_answer_chunks.append(chunk)
                        yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
                    yield f"data: {json.dumps({'type': 'tool_calling', 'tool_response': tool_response})}\n\n"
                    # print(tool_response)
            ai_response = "".join(ai_answer_chunks)
        except Exception as e:
            print(e)
            ai_response = "Tama is in High Demand, Please Try Again in Few Minutes"
            yield f"data: {json.dumps({'type': 'message_delta', 'content': ai_response})}\n\n"

        yield f"data: {json.dumps({'type': 'status', 'content': 'completed'})}\n\n"
        # print(ai_response)
        message_obj = await sync_to_async(Message.objects.create)(
        thread=thread,
        user_question=user_question,
        ai_answer=ai_response,
        therapist=tool_response
        )
        thread.is_book_couch = is_book_couch
        thread.last_conversation = message_obj.created
        if reasons_list:
        # Add categories to the thread asynchronously
            await sync_to_async(thread.add_categories_to_thread)(thread, reasons_list)
        else:
        # Save the thread asynchronously
            await sync_to_async(thread.save)()

        yield f"data: {json.dumps({'type': 'status', 'content': 'finished'})}\n\n"

    def get_top_similar_documents(self, user_question):
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
        results = retriever.get_relevant_documents(user_question)
        context = "\n\n".join([doc.page_content for doc in results])
        return context


    def get_thread_messages(self,thread):
        messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
        messages = messages[::-1]
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(("user", msg['user_question']))
            formatted_messages.append(("assistant", msg['ai_answer']))
        return formatted_messages

    async def post(self, request, *args, **kwargs):

        serializer = TamaResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:        
                user_question = serializer.validated_data['user_question']
                thread_id = serializer.validated_data['thread_id']
                try:
                    thread = await sync_to_async(Thread.objects.get)(uuid=thread_id)
                except Thread.DoesNotExist:
                    return Response({"message": f"Thread:{thread_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
                messages = await sync_to_async(self.get_thread_messages)(thread)
                if thread.chatbot_type==ChatbotTypeChoices.emotional:
                    response = StreamingHttpResponse(self.emotional_gen_ai(messages,user_question,thread), content_type='text/event-stream')
                elif thread.chatbot_type==ChatbotTypeChoices.support:
                    doc=self.get_top_similar_documents(user_question)
                    response = StreamingHttpResponse(self.support_gen_ai(messages,user_question,thread,doc), content_type='text/event-stream')
                response['Cache-Control'] = 'no-cache'  
                response["X-Accel-Buffering"] = "no" 
                return response
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
                return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return  Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UrlScrapingAPIView(NonAuthenticatedAPIMixin, AppAPIView):

    def split_documents(self, docs: list) -> list:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.split_documents(docs)

    def post(self, request):
        """Post method for scraping URL(s) and storing in vector DB"""
        # breakpoint()
        url_list = request.data.get("url")
        if not url_list:
            return self.send_error_response({"error": "No URL provided"})

        urls = [url.strip() for url in url_list.split(",") if url.strip()]
        if not urls:
            return self.send_error_response({"error": "No valid URLs found"})

        total_chunks = 0
        errors = []

        for url in urls:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                errors.append(f"Invalid URL: {url}")
                continue

            try:
                loader = WebBaseLoader(url)
                documents = loader.load()
                text_chunks = self.split_documents(documents)
                metadatas = {"url": url}
                documents = [
                    Document(page_content=chunk.page_content, metadata=metadatas)
                    for chunk in text_chunks
                ]
                vector_store.add_documents(documents=documents)
                total_chunks += len(text_chunks)

            except Exception as e:
                errors.append(f"Failed to process {url}: {str(e)}")

        return self.send_response(
            {"total_chunks": total_chunks, "errors": errors}
        )