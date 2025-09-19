# video/views.py - Daily.co support যোগ করুন
import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import VideoCallSession
from .serializers import VideoCallSessionSerializer
from appointments.models import Appointment
from datetime import datetime, timedelta
import uuid

DAILY_API_KEY = "a386c589f01d7443fa9e0d3f034505d7ae6a9566b2b9c31f50096515d1846be6"

DAILY_API_BASE = 'https://api.daily.co/v1'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_daily_room(request, appointment_id):
    """
    Create a Daily.co room for video call
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check authorization
        user = request.user
        if user.user_type == 1 and appointment.patient != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 2 and appointment.doctor.user != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create Daily.co room
        room_name = f"healthcare-appointment-{appointment_id}-{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{DAILY_API_BASE}/rooms",
            headers={
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "name": room_name,
                "privacy": "private",
                "properties": {
                    "exp": int((datetime.now() + timedelta(hours=2)).timestamp()),
                    "enable_chat": True,
                    "enable_screenshare": True,
                    "start_video_off": False,
                    "start_audio_off": False,
                }
            }
        )
        
        if response.status_code == 200:
            room_data = response.json()
            
            # Create video session record
            video_session = VideoCallSession.objects.create(
                appointment=appointment,
                room_id=room_name,
                status='ongoing',
                start_time=datetime.now()
            )
            
            return Response({
                "room_name": room_name,
                "room_url": room_data['url'],
                "session_id": video_session.id,
                "message": "Daily.co room created successfully"
            })
        else:
            return Response({"error": "Failed to create Daily.co room"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)