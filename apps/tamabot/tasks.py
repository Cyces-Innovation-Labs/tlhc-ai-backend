# from celery import shared_task
# from apps.tamabot.models import Thread, Message
# from apps.tamabot.views.system_message import love_hope_system_template
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# import requests
# from typing import Optional, Literal, List
# from pydantic import BaseModel, Field


# class MentalHealthSupport(BaseModel):
#     councelling_for: Optional[Literal["individual_counselling", "child_counselling", "partner_counselling", "family_counselling"]] = Field(
#         default="individual_counselling", description="Type of counselling"
#     )
#     level_of_experience: Optional[Literal["basic", "advance", "expert"]] = Field(
#         default="basic", description="Experience level of the therapist"
#     )
#     reasons: Optional[List[Literal["Trauma", "Mental Illness", "Grief and Loss", "Anxiety", "Relationship Issues"]]] = Field(
#         default=None, description="Reasons for seeking therapy"
#     )


# @shared_task
# def generate_ai_message(thread_id, user_question):
#     try:
#         thread = Thread.objects.get(uuid=thread_id)
#         messages = thread.messages.order_by('-created').values('user_question', 'ai_answer')[:6]

#         formatted_messages = []
#         for msg in messages:
#             formatted_messages.append(("user", msg['user_question']))
#             formatted_messages.append(("assistant", msg['ai_answer']))

#         system_template = love_hope_system_template
#         prompt_template = ChatPromptTemplate.from_messages([
#             ('system', system_template),
#             *formatted_messages,
#             ('user', '{text}')
#         ])
#         model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
#         parser = StrOutputParser()
#         chain = prompt_template | model | parser
#         ai_response = chain.invoke({"text": user_question})

#         if 'therapy=individual_counselling' in ai_response:
#             llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
#             structured_llm = llm.with_structured_output(MentalHealthSupport)
#             a = structured_llm.invoke({"text": user_question})

#             url = "https://api-v2-staging.thelovehopecompany.com/api/therapist/generate-therapist-booking-link/"
#             headers = {"Content-Type": "application/json"}
#             params = {
#                 "counselling_type": a.councelling_for,
#                 "level_of_experience": a.level_of_experience,
#                 "reasons": ','.join(a.reasons) if a.reasons else None
#             }

#             response = requests.get(url, headers=headers, params=params)
#             if response.status_code == 200:
#                 print(response)
#                 breakpoint()
#                 therapist_data = response.json()
#                 ai_response = chain.invoke({
#                     "message": ai_response,
#                     "therapist_data": str(therapist_data)
#                 })

#         Message.objects.create(
#             thread=thread,
#             user_question=user_question,
#             ai_answer=ai_response
#         )
#         return ai_response
#     except Exception as e:
#         return str(e)


