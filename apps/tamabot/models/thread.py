from django.db import models
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel


class Thread(BaseModel):

    tag = models.CharField( max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    
class Message(BaseModel):
    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name='messages',**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_question = models.TextField()
    ai_answer = models.TextField()
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
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