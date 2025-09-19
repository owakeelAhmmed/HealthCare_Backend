from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoCallViewSet, generate_agora_token, start_video_call, end_video_call
from .views import create_daily_room, get_daily_token

router = DefaultRouter()
router.register('sessions', VideoCallViewSet, basename='video-session')

# video/urls.py
urlpatterns = [
    path('', include(router.urls)),
    path('generate-token/<int:appointment_id>/', generate_agora_token, name='generate-agora-token'),
    path('start-call/<int:appointment_id>/', start_video_call, name='start-video-call'),
    path('end-call/<int:session_id>/', end_video_call, name='end-video-call'),
    # Daily.co endpoints
    path('daily-room/<int:appointment_id>/', create_daily_room, name='create-daily-room'),
    path('daily-token/<int:appointment_id>/', get_daily_token, name='get-daily-token'),
]