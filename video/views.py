from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import VideoCallSession
from appointments.models import Appointment
import uuid
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_agora_token(request, appointment_id):
    """
    Generate Agora token for video call
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if user has permission to join this call
        user = request.user
        if user.user_type == 1 and appointment.patient != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 2 and appointment.doctor.user != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create or get video session
        video_session, created = VideoCallSession.objects.get_or_create(
            appointment=appointment,
            defaults={'room_id': f"room_{uuid.uuid4().hex[:10]}"}
        )
        
        # In a real implementation, you would generate Agora token here
        # For now, we'll return the room ID
        return Response({
            "room_id": video_session.room_id,
            "appointment_id": appointment.id,
            "message": "Use this room_id to join the video call"
        })
        
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_video_call(request, appointment_id):
    """
    Start a video call session
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check authorization
        user = request.user
        if user.user_type not in [1, 2]:  # Only patients and doctors
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create video session
        room_id = f"room_{uuid.uuid4().hex[:10]}"
        video_session = VideoCallSession.objects.create(
            appointment=appointment,
            room_id=room_id,
            status='ongoing',
            start_time=datetime.now()
        )
        
        return Response({
            "room_id": room_id,
            "session_id": video_session.id,
            "message": "Video call started successfully"
        })
        
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_video_call(request, session_id):
    """
    End a video call session
    """
    try:
        video_session = VideoCallSession.objects.get(id=session_id)
        
        # Check authorization
        user = request.user
        appointment = video_session.appointment
        if user.user_type == 1 and appointment.patient != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 2 and appointment.doctor.user != user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Update session
        video_session.status = 'completed'
        video_session.end_time = datetime.now()
        video_session.save()
        
        return Response({
            "message": "Video call ended successfully",
            "duration": (video_session.end_time - video_session.start_time).total_seconds() if video_session.end_time else 0
        })
        
    except VideoCallSession.DoesNotExist:
        return Response({"error": "Video session not found"}, status=status.HTTP_404_NOT_FOUND)