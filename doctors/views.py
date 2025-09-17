from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Doctor
from .serializers import DoctorSerializer
from rest_framework.response import Response
# Create your views here.


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


    # def create(self, request, *args, **kwargs):
    #     user_id = request.data.get('user')
    #     if not user_id:
    #         return Response({'error': 'user_id is required'}, status=400)
        
    #     if Doctor.objects.filter(user_id=user_id).exists():
    #         return Response({'error': 'This user already has a doctor profile'}, status=400)

    #     return super().create(request, *args, **kwargs)

