from django.db import models
import uuid
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel

class Thread(BaseModel):
    pass
    
class AdminUser(BaseModel):

    first_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    last_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    phone_number = AppPhoneNumberField(unique=True)
    
class FeedBack(BaseModel):

    feedback_given_by = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    feedback = models.TextField()

class Message(BaseModel):
    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name='messages',**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_question = models.TextField()
    ai_answer = models.TextField()
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
    feedback = models.ForeignKey(FeedBack, on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    # conversations = models.JSONField(default=list)

    # def add_conversations(self, human, ai):
    #     """Add a new message to the thread"""

    #     self.conversations.append({
    #         'role': 'user',
    #         'content': human,
    #     })
    #     self.conversations.append({
    #         'role': 'assistant',
    #         'content': ai,
    #     })
    #     self.save()