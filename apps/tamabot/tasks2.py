# from celery import shared_task
# from apps.tamabot.models import Thread, Message




# from apps.tamabot.views.system_message import love_hope_system_template
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# import requests
# from apps.tamabot.models import Thread,Message 


# from typing import Optional,Literal, List
# from pydantic import BaseModel, Field


# class MentalHealthSupport(BaseModel):
#     """Schema for selecting professional mental health support options for Booking."""

#     councelling_for: Optional[Literal["individual_counselling", "child_counselling", "partner_counselling","family_counselling"]] = Field(
#         default="individual_counselling",  # default to "feature_a"
#         description="Determines the type of councelling  for the user"
#     )
    
#     level_of_experience: Optional[Literal[ "basic","advance","expert"]]=Field(
#           default="basic", description="Expectation of therapist level of experience by the user"
#     )
#     reasons:Optional[List[Literal[ "Trauma","Mental Illness","Grief and Loss","Anxiety","Relationship Issues"]]]=Field(
#           default=None, description="fetch the Reasons for the user's problems as much as possible"
#     )

# @shared_task
# def generate_ai_message(thread_id,user_question):  
#     thread = Thread.objects.get(uuid=thread_id)    
#     messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]
#     formatted_messages = []
#     for msg in messages:
#         formatted_messages.append(("user", msg['user_question']))
#         formatted_messages.append(("assistant", msg['ai_answer']))
#     system_template=love_hope_system_template
    
#     prompt_template = ChatPromptTemplate.from_messages([
#     ('system', system_template),
#     *formatted_messages,
#     ('user', '{text}')
#         ])
#     model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
#     parser = StrOutputParser()
#     chain = prompt_template | model | parser
#     ai_response=chain.invoke({"text": user_question })
    
#     if 'https://thelovehopecompany.com/book-therapy/therapy-for?therapy=individual_counselling' in ai_response:
#         llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)
#         structured_llm = llm.with_structured_output(MentalHealthSupport)
#         new_question = ('user',user_question)
#         formatted_messages.append(new_question)
#         a=structured_llm.invoke(f'{formatted_messages}')
#         url = "https://api-v2-staging.thelovehopecompany.com/api/therapist/generate-therapist-booking-link/"
#         headers = {
#             "Content-Type": "application/json"
#         }
#         if a.reasons:
#             reasons_param = ','.join(a.reasons)
#         else:
#             reasons_param = None
#         params = {
#             "counselling_type": a.councelling_for,    
#             "level_of_experience": a.level_of_experience, 
#             "reasons": reasons_param,                         
#         }

#         response = requests.get(url, headers=headers, params=params)
#         if response.status_code==200:
#             system_template = """
#             Message : {message}
#             Therapist Data : {therapist_data}
            
#             Display The Message Fully and suggest the therapists to users  
#             Display The Therapist Details In Tabular Format Like name,Therapist link
            
#             Important : If there is no therpist  simply show the Message alone  
#             """
#             prompt_template = ChatPromptTemplate.from_messages([
#                 ('system', system_template),
#             ])
#             model = ChatOpenAI(model="gpt-4o-mini",temperature=0.4)

#             parser = StrOutputParser()

#             chain = prompt_template | model | parser

#             ai_response=chain.invoke({"message": ai_response, "therapist_data": str(response.json())})

#         Message.objects.create(
#         thread=thread,
#         user_question=user_question,
#         ai_answer=ai_response,
#         )
#         return ai_response
    
