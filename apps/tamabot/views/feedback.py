from apps.common.views import AppModelCUDAPIViewSet, RemoteJWTAuthentication, AppModelListAPIViewSet, AppModelUpdateAPIViewSet
from apps.tamabot.models import Feedback, Thread
from apps.tamabot.serializers import FeedbackCUDSerializer, FeedbackDetailSerializer,ThreadTagUpdateSerializer, ThreadStatusUpdateSerializer

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
    
    def get_queryset(self):

        thread = self.request.query_params.get('thread') 
        if thread:
            return super().get_queryset().filter(thread__uuid=thread)
        return Feedback.objects.none() 

class ThreadTagUpdateViewSet(AppModelUpdateAPIViewSet):
    """API to update thread Tag """

    authentication_classes = [RemoteJWTAuthentication]
    queryset = Thread.objects.all()
    serializer_class = ThreadTagUpdateSerializer


class ThreadStatusUpdateViewSet(AppModelUpdateAPIViewSet):
    """API to update thread Tag """

    authentication_classes = [RemoteJWTAuthentication]
    queryset = Thread.objects.all()
    serializer_class = ThreadStatusUpdateSerializer