from django.urls import path
from . import views

urlpatterns = [
    path('stream-channel/<int:appointment_id>/', views.create_stream_channel, name='create_stream_channel'),
    path('stream-token/<int:appointment_id>/', views.generate_stream_token, name='generate_stream_token'),
    path('start-call/<int:appointment_id>/', views.start_video_call, name='start_video_call'),
    path('end-call/<int:appointment_id>/', views.end_video_call, name='end_video_call'),
]