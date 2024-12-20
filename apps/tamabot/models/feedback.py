from django.db import models
from apps.common.models.base import BaseModel
from apps.common.models import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel

class AdminUser(BaseModel):

    first_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    last_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,)
    user_id = models.IntegerField(unique=True)
    
class Feedback(BaseModel):
    from apps.tamabot.models.thread import Thread

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="related_thread_feedbacks")
    feedback_given_by = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    feedback = models.TextField()