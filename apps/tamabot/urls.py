from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.tamabot.views import (   
    NewThreadAPIView,
    TamaResponseAPIView,
    ListThreadsViewSet,
    TamaStreamingResponseAPIView,
    FeedbackCUDAPIView,
    FeedbackDetailAPIAPIViewSet,
    ThreadTagUpdateViewSet,
    MessageListAPIViewSet
)

router = SimpleRouter()
API_URL_PREFIX = "api/chatbot/"

router.register("threads/list", ListThreadsViewSet)
router.register("get_message/list", MessageListAPIViewSet)
router.register("feedback/cud", FeedbackCUDAPIView)
router.register("feedback/detail",FeedbackDetailAPIAPIViewSet)
router.register("thread/tag/update", ThreadTagUpdateViewSet)

urlpatterns = [
    path(f"{API_URL_PREFIX}tama-streaming-response/", TamaStreamingResponseAPIView.as_view()),
    path(f"{API_URL_PREFIX}new-thread/", NewThreadAPIView.as_view()),
    path(f"{API_URL_PREFIX}tama-response/", TamaResponseAPIView.as_view()),
    path(f"{API_URL_PREFIX}", include(router.urls)),
]