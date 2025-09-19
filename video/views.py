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

# Daily.co API Key (এটি আপনার environment variable থেকে নিন)
DAILY_API_KEY ='a386c589f01d7443fa9e0d3f034505d7ae6a9566b2b9c31f50096515d1846be6'
DAILY_API_BASE = 'https://api.daily.co/v1'

class VideoCallViewSet(viewsets.ModelViewSet):
    queryset = VideoCallSession.objects.all()
    serializer_class = VideoCallSessionSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_daily_room(request, appointment_id):
    """
    Create a Daily.co room for video call
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check authorization - patient or doctor
        user = request.user
        if user.user_type == 1 and appointment.patient != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 2 and appointment.doctor.user != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create unique room name
        room_name = f"appointment-{appointment_id}-{uuid.uuid4().hex[:8]}"
        
        # Create room on Daily.co
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
            
            # Create or update video session record
            video_session, created = VideoCallSession.objects.update_or_create(
                appointment=appointment,
                defaults={
                    'room_id': room_name,
                    'status': 'scheduled',
                    'start_time': None,
                    'end_time': None
                }
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_token(request, appointment_id):
    """
    Generate Daily.co meeting token for additional security
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check authorization
        user = request.user
        if user.user_type == 1 and appointment.patient != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 2 and appointment.doctor.user != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get video session
        video_session = VideoCallSession.objects.get(appointment=appointment)
        
        # Generate meeting token
        response = requests.post(
            f"{DAILY_API_BASE}/meeting-tokens",
            headers={
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "properties": {
                    "room_name": video_session.room_id,
                    "user_id": str(user.id),
                    "user_name": user.get_full_name(),
                    "is_owner": True,
                    "exp": int((datetime.now() + timedelta(hours=2)).timestamp())
                }
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return Response({
                "token": token_data['token'],
                "room_name": video_session.room_id
            })
        else:
            return Response({"error": "Failed to generate token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except (Appointment.DoesNotExist, VideoCallSession.DoesNotExist):
        return Response({"error": "Appointment or video session not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_video_call(request, appointment_id):
    """
    Mark video call as started
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        video_session = VideoCallSession.objects.get(appointment=appointment)
        
        # Update status and start time
        video_session.status = 'ongoing'
        video_session.start_time = datetime.now()
        video_session.save()
        
        return Response({"message": "Video call started", "status": "ongoing"})
        
    except (Appointment.DoesNotExist, VideoCallSession.DoesNotExist):
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_video_call(request, appointment_id):
    """
    Mark video call as completed
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        video_session = VideoCallSession.objects.get(appointment=appointment)
        
        # Update status and end time
        video_session.status = 'completed'
        video_session.end_time = datetime.now()
        video_session.save()
        
        return Response({"message": "Video call ended", "status": "completed"})
        
    except (Appointment.DoesNotExist, VideoCallSession.DoesNotExist):
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)