from rest_framework import serializers
from .models import Doctor
from accounts.models import User
from accounts.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    available_hours = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user_details",
            "specialization",
            "experience",
            "bio",
            "consultation_fee",
            "available_days",
            "available_time_start",
            "available_time_end",
            "available_hours",
            "address",
            "phone",
            "email"
        ]
        read_only_fields = ['id']

    def get_available_hours(self, obj):
        return obj.available_hours

class DoctorCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type=2),
        write_only=True,
        source='user'
    )

    class Meta:
        model = Doctor
        fields = [
            "user_id",
            "specialization",
            "experience",
            "bio",
            "consultation_fee",
            "available_days",
            "available_time_start",
            "available_time_end",
            "address",
            "phone",
            "email"
        ]

    def validate_user_id(self, value):
        if Doctor.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a doctor profile")
        return value