# doctors/serializers.py
from rest_framework import serializers
from .models import Doctor
from accounts.serializers import UserSerializer
from accounts.models import User

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=2),  # শুধু Doctor type user
        source='user',
        write_only=True
    )

    class Meta:
        model = Doctor
        fields = '__all__'
