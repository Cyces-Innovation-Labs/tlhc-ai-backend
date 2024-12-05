from apps.common.views import AppAPIView,NonAuthenticatedAPIMixin,AppModelListAPIViewSet
from apps.tamabot.models import Thread,Message 
from apps.tamabot.serializers import TamaResponseSerializer,MessageFeedbackSerializer


from .system_message import love_hope_system_template
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from django.http import StreamingHttpResponse
from typing import Optional,Literal, List
from pydantic import BaseModel, Field
import requests
from uuid import UUID
from apps.common.serializers import AppReadOnlyModelSerializer
from django.conf import settings
# from rest_framework import serializers

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
            formatted_messages = []
            for msg in messages:
                formatted_messages.append(("user", msg['user_question']))
                formatted_messages.append(("assistant", msg['ai_answer']))
            system_template=love_hope_system_template
            print(formatted_messages)
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
    


    
class MessageSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = Message
        fields = ['uuid', 'user_question', 'ai_answer','like','dislike']


class RetrieveMessageAPIView(NonAuthenticatedAPIMixin,AppAPIView):
    def get(self, request, thread_uuid: UUID):
        try:
            thread = Thread.objects.get(uuid=thread_uuid)
        except Thread.DoesNotExist:
            return self.send_error_response({"error": "Invalid thread ID"})
        messages = thread.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return self.send_response({"message": serializer.data})
    
class ThreadListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for Location list."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Thread
        fields = ["uuid", "created"]

    
class ListThreadsViewSet(NonAuthenticatedAPIMixin,AppModelListAPIViewSet):

    queryset = Thread.objects.all()
    serializer_class = ThreadListSerializer

    def get_meta_for_table(self) -> dict:
        data = {
            "columns": self.get_table_columns()
        }
        return data

        
        

class FeedbackMessageAPIView(NonAuthenticatedAPIMixin,AppAPIView):
    def post(self, request, *args, **kwargs):
        serializer = MessageFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            message_uuid = serializer.validated_data['message_uuid']
            like = serializer.validated_data['like']
            dislike = serializer.validated_data['dislike']
            try:
                # Fetch the message by its UUID
                message = Message.objects.get(uuid=message_uuid)
                if like and dislike:
                    return self.send_error_response({'error': 'You cannot like and dislike the same message.'})
               
                
                message.like = like
                message.dislike = dislike
                message.save()
                return self.send_response({'message': 'Feedback successfully recorded'})
            except Message.DoesNotExist:
                # If the message does not exist
                return self.send_error_response({'error': 'Message not found'})
        return self.send_error_response(serializer.errors)
                




# class FeedbackMessageAPIView(NonAuthenticatedAPIMixin,AppAPIView):
#     def post(self, request, *args, **kwargs):
#         serializer = FeedbackSerializer(data=request.data)

#         try:
#             # Fetch the message by its UUID
            
#             message = Message.objects.get(uuid=message_uuid)
            
#             # Serialize the data for updating
#             serializer = FeedbackSerializer(message, data=request.data, partial=True)
            
#             if serializer.is_valid():
#                 # Save the updated fields
#                 serializer.save()
#                 return self.send_response({"success": True, "message": "Feedback updated successfully."})
#             else:
#                 return self.send_error_response({"success": False, "errors": serializer.errors})
        
#         except Message.DoesNotExist:
#             return self.send_error_response({"success": False, "error": "Message not found."})


    # def generate_data(self, text,thread_id):
    #     system_template = love_hope_system_template
    #     prompt_template = ChatPromptTemplate.from_messages([
    #         ('system', system_template),
    #         ('user', '{text}')
    #     ])
    #     model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, streaming=True)
    #     parser = StrOutputParser()
    #     chain = prompt_template | model | parser
    #     ai_answer_chunks = []
    #     for chunk in chain.stream({"text": text}):
    #         ai_answer_chunks.append(chunk.strip())
    #         yield f"{chunk}"
    #     ai_answer = "".join(ai_answer_chunks)
    #     thread = Thread.objects.get(uuid=thread_id)
    #     Message.objects.create(
    #         thread=thread,
    #         user_question=text,
    #         ai_answer=ai_answer
    #     )
        # save_ai_response_task.delay(thread_id, text, ai_answer)

    # serialized_messages = MessageSerializer(messages, many=True).data
    # return self.send_response(serialized_messages)
    # response = StreamingHttpResponse(self.generate_data(user_question,thread_id), content_type='text/event-stream')
    # response['Cache-Control'] = 'no-cache'  
    # response["X-Accel-Buffering"] = "no"
    
    # return response

