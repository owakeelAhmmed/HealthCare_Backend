from rest_framework import serializers
from .models import Appointment
from doctors.serializers import DoctorSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']  # status এখানে রাখবেন না
