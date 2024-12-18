from apps.common.serializers import AppWriteOnlyModelSerializer, AppReadOnlyModelSerializer, AppUpdateModelSerializer
from apps.tamabot.models import Feedback, Thread
from rest_framework import serializers


class FeedbackCUDSerializer(AppWriteOnlyModelSerializer):
    """Common write serializer for Feedback for message"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Feedback
        fields = [
            "thread",
            "feedback",
        ]
    
    def create(self, validated_data):
        """
        Create a Feedback instance and associate it with the message.
        """

        user = self.get_user().user
        validated_data["feedback_given_by"]=user
        feedback = Feedback.objects.create(**validated_data)
        return feedback
    
class FeedbackDetailSerializer(AppReadOnlyModelSerializer):
    """Serializer to create BAC Feedback List Serializer"""

    created = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p", allow_null=True)
    feedback_given_by = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Feedback
        fields = [
            "id",
            "uuid",
            "thread",
            "feedback",
            "feedback_given_by",
            "created",
        ]

    def get_feedback_given_by(self, obj):
        if obj.feedback_given_by:
            return f"{obj.feedback_given_by.first_name} {obj.feedback_given_by.last_name}"
        return None

class ThreadTagUpdateSerializer(AppUpdateModelSerializer):
    """Add Tag Against Thread"""

    class Meta(AppUpdateModelSerializer.Meta):
        model = Thread
        fields = ["tag"]