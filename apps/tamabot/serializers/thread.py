
from rest_framework import serializers



class TamaResponseSerializer(serializers.Serializer):
    thread_id = serializers.UUIDField(required=True)
    user_question = serializers.CharField(max_length=512, required=True)

class MessageFeedbackSerializer(serializers.Serializer):
    message_uuid = serializers.UUIDField(required=True)
    like=serializers.BooleanField(required=True)
    dislike=serializers.BooleanField(required=True)