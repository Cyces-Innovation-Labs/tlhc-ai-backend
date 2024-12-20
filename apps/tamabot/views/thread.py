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


book_couch_link = settings.BOOK_COUCH_LINK
therapist_url = settings.THERAPIST_URL


class MentalHealthSupport(BaseModel):
    """Schema for selecting professional mental health support options for Booking."""

    councelling_for: Optional[Literal["individual_counselling", "child_counselling", "partner_counselling","family_counselling"]] = Field(
        default="individual_counselling",  # default to "feature_a"
        description="Determines the type of councelling  for the user"
    )
    
    level_of_experience: Optional[Literal[ "basic","advance","expert"]]=Field(
          default="basic", description="Expectation of therapist level of experience by the user"
    )
    reasons:Optional[List[Literal[ "Trauma","Mental Illness","Grief and Loss","Anxiety","Relationship Issues"]]]=Field(
          default=None, description="fetch the Reasons for the user's problems as much as possible"
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

    
class TamaResponseAPIView(NonAuthenticatedAPIMixin,AppAPIView):

    def post(self, request, *args, **kwargs):
        """Handle POST request to for Tama answers """
        serializer = TamaResponseSerializer(data=request.data)
        if serializer.is_valid():
            user_question = serializer.validated_data['user_question']
            thread_id = serializer.validated_data['thread_id']
            try:
                thread = Thread.objects.get(uuid=thread_id)
            except Thread.DoesNotExist:
                return self.send_error_response({"error": "Invalid thread ID"})    
            messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
            messages = messages[::-1]
            formatted_messages = []
            for msg in messages:
                formatted_messages.append(("user", msg['user_question']))
                formatted_messages.append(("assistant", msg['ai_answer']))
            system_template=love_hope_system_template
            
            prompt_template = ChatPromptTemplate.from_messages([
            ('system', system_template),
            *formatted_messages,
            ('user', '{text}')
                ])
            model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
            parser = StrOutputParser()
            chain = prompt_template | model | parser
            ai_response=chain.invoke({"text": user_question })
            
            if book_couch_link in ai_response:
                llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)
                structured_llm = llm.with_structured_output(MentalHealthSupport)
                new_question = ('user',user_question)
                formatted_messages.append(new_question)
                a=structured_llm.invoke(f'{formatted_messages}')
                url = therapist_url
                headers = {
                    "Content-Type": "application/json"
                }
                if a.reasons:
                    reasons_param = ','.join(a.reasons)
                else:
                    reasons_param = None
                params = {
                    "counselling_type": a.councelling_for,    
                    "level_of_experience": a.level_of_experience, 
                    "reasons": reasons_param,                         
                }

                response = requests.get(url, headers=headers, params=params)
                if response.status_code==200:
                    system_template = """
                    Message : {message}
                    Therapist Data : {therapist_data}
                    
                    Display The Message Fully and suggest the therapists to users  
                    Display The Therapist Details In Tabular Format Like name,Therapist link
                    
                    Important : If there is no therpist  simply show the Message alone  
                    """
                    prompt_template = ChatPromptTemplate.from_messages([
                        ('system', system_template),
                    ])
                    model = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)

                    parser = StrOutputParser()

                    chain = prompt_template | model | parser

                    ai_response=chain.invoke({"message": ai_response, "therapist_data": str(response.json())})

            Message.objects.create(
                thread=thread,
                user_question=user_question,
                ai_answer=ai_response,
                )
            
            return self.send_response({"ai_answer":ai_response})
        return self.send_error_response({"message":serializer.errors})
    
    

class ListThreadsViewSet(NonAuthenticatedAPIMixin,AppModelListAPIViewSet):

    queryset = Thread.objects.filter(messages__isnull=False).distinct().order_by("-created")
    serializer_class = ThreadListSerializer
    filterset_fields = ["uuid"] 

    all_table_columns = {
        "uuid": "Conversation ID",
        "categories": "Category",
        "is_book_couch": "Book a couch",
        "created": "Start Date",
        "modified": "End Date",
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
        if thread_id:
            q=super().get_queryset()
            return q.filter(thread__uuid=thread_id)
        return Message.objects.none() 


class TamaStreamingResponseAPIView(NonAuthenticatedAPIMixin,AppAPIView):

    def gen_ai(self,formatted_messages,user_question,thread):
        system_template=love_hope_system_template_V2
        
        prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        *formatted_messages,
        ('user', '{text}')
            ])
        yield f"data: {json.dumps({'type': 'status', 'content': 'started'})}\n\n"
        model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
        parser = StrOutputParser()
        chain = prompt_template | model | parser
        ai_answer_chunks = []
        for chunk in chain.stream({"text": user_question }):
            ai_answer_chunks.append(chunk)
            yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
            
        
        ai_response = "".join(ai_answer_chunks)
         
        if book_couch_link in ai_response:
            thread.is_book_couch = True
            thread.save()
            llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)
            structured_llm = llm.with_structured_output(MentalHealthSupport)
            new_question = ('user',user_question)
            formatted_messages.append(new_question)
            a=structured_llm.invoke(f'{formatted_messages}')
            url = therapist_url
            headers = {
                "Content-Type": "application/json"
            }
            if a.reasons:
                
                thread.add_categories_to_thread(thread,a.reasons)
                reasons_param = ','.join(a.reasons)
            else:
                reasons_param = None
            params = {
                "counselling_type": a.councelling_for,    
                "level_of_experience": a.level_of_experience, 
                "reasons": reasons_param,                         
            }
            
            # yield f"data: {json.dumps({'type': 'status', 'content': 'fetching_therapist'})}\n\n"
            response = requests.get(url, headers=headers, params=params)
            if response.status_code==200:
                data = response.json()
                therapist_data = data.get('data', {}).get('results', [])
                if therapist_data:
                    system_template = """
                    you'r only role is to display data in nice format don't use Tabular format
                    Suggested Therapist Data : {therapist_data}
                    Display The Therapist Details In Readable Format Like Suggested Therapist name,Therapist link
                    Important : If there is no therpist data available simply return 'Visit The Love Hope Company for Therapist'
                    """
                    prompt_template = ChatPromptTemplate.from_messages([
                        ('system', system_template),
                    ])
                    model = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)

                    parser = StrOutputParser()

                    chain = prompt_template | model | parser
                    ai_table_chunks=[]
                    new_chunk="\n\n"
                    yield f"data: {json.dumps({'type': 'message_delta', 'content': new_chunk})}\n\n"
                    for chunk in chain.stream({"therapist_data": str(therapist_data)}):
                        ai_table_chunks.append(chunk)
                        yield f"data: {json.dumps({'type': 'message_delta', 'content': chunk})}\n\n"
                    ai_table_response = "".join(ai_table_chunks)
                    ai_response=f"{ai_response}\n\n{ai_table_response}"

        Message.objects.create(
                thread=thread,
                user_question=user_question,
                ai_answer=ai_response,
                )
        yield f"data: {json.dumps({'type': 'status', 'content': 'finished'})}\n\n"

        
    


    def post(self, request, *args, **kwargs):
        """Handle POST request to for Tama answers """
        serializer = TamaResponseSerializer(data=request.data)
        if serializer.is_valid():
            user_question = serializer.validated_data['user_question']
            thread_id = serializer.validated_data['thread_id']
            try:
                thread = Thread.objects.get(uuid=thread_id)
            except Thread.DoesNotExist:
                return self.send_error_response({"error": "Invalid thread ID"})    
            messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
            messages = messages[::-1]
            formatted_messages = []
            for msg in messages:
                formatted_messages.append(("user", msg['user_question']))
                formatted_messages.append(("assistant", msg['ai_answer']))
            response = StreamingHttpResponse(self.gen_ai(formatted_messages,user_question,thread), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'  
            response["X-Accel-Buffering"] = "no" 
            return response
        return self.send_error_response({"message":serializer.errors})
