from django.db import models


from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH, COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, BaseModel
from apps.tamabot.config import StatusChoices


class Thread(BaseModel):

    tag = models.CharField( max_length=COMMON_CHAR_FIELD_MAX_LENGTH,**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    #faizermodel
    is_book_couch=models.BooleanField(default=False)
    categories =models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=StatusChoices.choices,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    last_conversation=models.DateTimeField(null=True, blank=True)


    def add_categories_to_thread(self,thread, new_categories):
        # Combine existing and new categories, ensuring no duplicates
        thread.categories = list(set(thread.categories + new_categories))
        thread.save()

    

    
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