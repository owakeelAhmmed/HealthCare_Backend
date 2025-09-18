from rest_framework import serializers
from .models import VideoCallSession
from appointments.serializers import AppointmentSerializer

class VideoCallSessionSerializer(serializers.ModelSerializer):
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = VideoCallSession
        fields = '__all__'