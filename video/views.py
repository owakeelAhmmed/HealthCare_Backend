import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stream_chat import StreamChat
from appointments.models import Appointment
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

# Stream.io credentials
STREAM_API_KEY = config('STREAM_API_KEY')
STREAM_API_SECRET = config('STREAM_API_SECRET')

# Initialize Stream.io client
stream_client = StreamChat(api_key=STREAM_API_KEY, api_secret=STREAM_API_SECRET)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stream_channel(request, appointment_id):
    """
    Create a Stream.io video call channel for an appointment
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if user has permission to access this appointment
        if request.user not in [appointment.patient, appointment.doctor.user]:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create channel ID
        channel_id = f"video_call_{appointment_id}"
        
        # Create channel members (doctor and patient)
        doctor_id = f"doctor_{appointment.doctor.id}"
        patient_id = f"patient_{appointment.patient.id}"
        
        # Create or get channel
        channel = stream_client.channel(
            "messaging", 
            channel_id,
            {
                "name": f"Video Call - Appointment #{appointment_id}",
                "members": [doctor_id, patient_id],
                "created_by_id": patient_id if request.user == appointment.patient else doctor_id,
                "custom": {
                    "appointment_id": appointment_id,
                    "type": "video_call",
                    "doctor_name": f"Dr. {appointment.doctor.user.get_full_name()}",
                    "patient_name": appointment.patient.get_full_name(),
                    "consultation_fee": str(appointment.doctor.consultation_fee)
                }
            }
        )
        
        # Create the channel
        channel.create(request.user.username or str(request.user.id))
        
        return Response({
            'channel_id': channel_id,
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'appointment_id': appointment_id
        })
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_stream_token(request, appointment_id):
    """
    Generate Stream.io token for video call
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if user has permission
        if request.user not in [appointment.patient, appointment.doctor.user]:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Determine user role and ID
        if request.user == appointment.patient:
            user_id = f"patient_{appointment.patient.id}"
            user_role = "patient"
        else:
            user_id = f"doctor_{appointment.doctor.id}"
            user_role = "doctor"
        
        # Generate token
        token = stream_client.create_token(user_id)
        
        return Response({
            'token': token,
            'user_id': user_id,
            'api_key': STREAM_API_KEY,
            'appointment_id': appointment_id,
            'user_role': user_role
        })
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_video_call(request, appointment_id):
    """
    Start video call session
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Update appointment status
        appointment.status = 'in_progress'
        appointment.save()
        
        return Response({
            'message': 'Video call started',
            'appointment_id': appointment_id,
            'status': appointment.status
        })
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_video_call(request, appointment_id):
    """
    End video call session
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Update appointment status
        appointment.status = 'completed'
        appointment.save()
        
        return Response({
            'message': 'Video call ended',
            'appointment_id': appointment_id,
            'status': appointment.status
        })
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )