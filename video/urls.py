from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoCallViewSet

router = DefaultRouter()
router.register('sessions', VideoCallViewSet, basename='video-session')

urlpatterns = [
    path('', include(router.urls)),
]