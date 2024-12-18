from apps.common.views import AppModelCUDAPIViewSet, RemoteJWTAuthentication, AppModelListAPIViewSet, AppModelUpdateAPIViewSet, NonAuthenticatedAPIMixin
from apps.tamabot.models import Feedback, Thread
from apps.tamabot.serializers import FeedbackCUDSerializer, FeedbackDetailSerializer,ThreadTagUpdateSerializer

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
    filterset_fields = ["thread"] 

class ThreadTagUpdateViewSet(NonAuthenticatedAPIMixin, AppModelUpdateAPIViewSet):
    """API to update thread Tag """

    authentication_classes = [RemoteJWTAuthentication]
    queryset = Thread.objects.all()
    serializer_class = ThreadTagUpdateSerializer