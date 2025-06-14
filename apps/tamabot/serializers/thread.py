from rest_framework import serializers
from apps.tamabot.config import ChatbotTypeChoices
from apps.tamabot.models import Thread,Message
from apps.common.serializers import AppReadOnlyModelSerializer

class TamaResponseSerializer(serializers.Serializer):
    thread_id = serializers.UUIDField(required=True)
    user_question = serializers.CharField(max_length=512, required=True)

class ThreadCreateSerializer(serializers.Serializer):
    chatbot_type = serializers.ChoiceField(choices=ChatbotTypeChoices.choices, required=True)

class MessageSerializer(AppReadOnlyModelSerializer):
    class Meta:
        model = Message
        fields = ['uuid', 'user_question', 'ai_answer','created','therapist']


class ThreadListSerializer(AppReadOnlyModelSerializer):
    """Serializer class for Location list."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Thread
        fields = ["uuid","id", "categories","is_book_couch","created","modified","status","tag","last_conversation"]