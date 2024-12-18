from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.tamabot.views import NewThreadAPIView,TamaResponseAPIView,RetrieveMessageAPIView,FeedbackMessageAPIView,ListThreadsViewSet, FeedbackCUDAPIView, FeedbackDetailAPIAPIViewSet

router = SimpleRouter()
API_URL_PREFIX = "api/chatbot/"

router.register("threads/list", ListThreadsViewSet)
router.register("feedback/cud", FeedbackCUDAPIView)
router.register("feedback/detail",FeedbackDetailAPIAPIViewSet)

urlpatterns = [
   
    path(f"{API_URL_PREFIX}new-thread/", NewThreadAPIView.as_view()),
    path(f"{API_URL_PREFIX}tama-response/", TamaResponseAPIView.as_view()),
    path(f"{API_URL_PREFIX}get-message/<uuid:thread_uuid>/", RetrieveMessageAPIView.as_view()),
    path(f"{API_URL_PREFIX}feedback-message/", FeedbackMessageAPIView.as_view(), name="Feedback"),
    path(f"{API_URL_PREFIX}", include(router.urls)),
]