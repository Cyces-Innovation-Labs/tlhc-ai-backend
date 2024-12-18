from apps.common.views import AppModelCUDAPIViewSet, RemoteJWTAuthentication, AppModelListAPIViewSet
from apps.tamabot.models import Feedback
from apps.tamabot.serializers import FeedbackCUDSerializer, FeedbackDetailSerializer

class FeedbackCUDAPIView(AppModelCUDAPIViewSet):
    """API to add Feedback to an existing message"""

    authentication_classes = [RemoteJWTAuthentication]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackCUDSerializer

class FeedbackDetailAPIAPIViewSet(AppModelListAPIViewSet):
    """API to list all Feedback against message"""

    authentication_classes = [RemoteJWTAuthentication]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackDetailSerializer
    filterset_fields = ["message"] 
