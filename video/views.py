from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VideoCallSession
from .serializers import VideoCallSessionSerializer
import uuid
from datetime import datetime

class VideoCallViewSet(viewsets.ModelViewSet):
    queryset = VideoCallSession.objects.all()
    serializer_class = VideoCallSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 1:  # Patient
            return VideoCallSession.objects.filter(appointment__patient=user)
        elif user.user_type == 2:  # Doctor
            return VideoCallSession.objects.filter(appointment__doctor__user=user)
        elif user.user_type == 3:  # Admin
            return VideoCallSession.objects.all()
        return VideoCallSession.objects.none()
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        appointment_id = request.data.get('appointment_id')
        
        try:
            from appointments.models import Appointment
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check if user has permission to create session for this appointment
            user = request.user
            if user.user_type == 1 and appointment.patient != user:
                return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            elif user.user_type == 2 and appointment.doctor.user != user:
                return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
            # Create unique room ID
            room_id = f"room_{uuid.uuid4().hex[:10]}"
            
            # Create video session
            video_session = VideoCallSession.objects.create(
                appointment=appointment,
                room_id=room_id
            )
            
            serializer = self.get_serializer(video_session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def start_call(self, request, pk=None):
        video_session = self.get_object()
        video_session.status = 'ongoing'
        video_session.start_time = datetime.now()
        video_session.save()
        
        return Response({"status": "call started", "room_id": video_session.room_id})
    
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        video_session = self.get_object()
        video_session.status = 'completed'
        video_session.end_time = datetime.now()
        video_session.save()
        
        return Response({"status": "call ended"})