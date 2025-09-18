from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoCallViewSet, generate_agora_token, start_video_call, end_video_call

router = DefaultRouter()
router.register('sessions', VideoCallViewSet, basename='video-session')

urlpatterns = [
    path('', include(router.urls)),
    
    # নতুন API endpoints যোগ করুন
    path('generate-token/<int:appointment_id>/', generate_agora_token, name='generate-agora-token'),
    path('start-call/<int:appointment_id>/', start_video_call, name='start-video-call'),
    path('end-call/<int:session_id>/', end_video_call, name='end-video-call'),
]