from django.urls import path
from .views import create_daily_room, get_daily_token, start_video_call, end_video_call

urlpatterns = [
    path('daily-room/<int:appointment_id>/', create_daily_room, name='create-daily-room'),
    path('daily-token/<int:appointment_id>/', get_daily_token, name='get-daily-token'),
    path('start-call/<int:appointment_id>/', start_video_call, name='start-video-call'),
    path('end-call/<int:appointment_id>/', end_video_call, name='end-video-call'),
]