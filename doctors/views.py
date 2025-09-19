from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer, DoctorCreateSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DoctorCreateSerializer
        return DoctorSerializer

    def get_queryset(self):
        # Patients can see all doctors
        if self.request.user.user_type == 1:  # Patient
            return Doctor.objects.all()
        # Doctors can only see themselves
        elif self.request.user.user_type == 2:  # Doctor
            return Doctor.objects.filter(user=self.request.user)
        # Admins can see all doctors
        elif self.request.user.user_type == 3:  # Admin
            return Doctor.objects.all()
        return Doctor.objects.none()

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        doctor = self.get_object()
        # Add your availability logic here
        return Response({
            'available': True,
            'doctor_id': doctor.id,
            'message': 'Availability check endpoint'
        })