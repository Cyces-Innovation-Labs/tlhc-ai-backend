from apps.common.views import AppAPIView,NonAuthenticatedAPIMixin,AppModelListAPIViewSet
from apps.tamabot.models import Thread,Message 
from apps.tamabot.serializers import TamaResponseSerializer,MessageSerializer,ThreadListSerializer
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


book_couch_link = settings.BOOK_COUCH_LINK
therapist_url = settings.THERAPIST_URL

class ThreadFilter(filters.FilterSet):
    categories = filters.CharFilter(method='filter_categories')
    class Meta:
        model = Thread
        fields = {
            'created': ['gte', 'lte'],
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
            thread = Thread.objects.create()
            thread_id = str(thread.uuid)
            return self.send_response({"thread_id": thread_id})
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

   
