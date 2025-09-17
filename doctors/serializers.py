from rest_framework import serializers
from .models import Doctor
from accounts.models import User
from accounts.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  
    user_select = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(user_type=2),
        write_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",                  
            "user_select",           
            "specialization",
            "experience",
            "bio",
            "consultation_fee",
            "available_days",
            "available_time_start",
            "available_time_end",
        ]

    def create(self, validated_data):
        user = validated_data.pop("user_select")
        if Doctor.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                {"user_select": "This user already has a doctor profile"}
            )
        return Doctor.objects.create(user=user, **validated_data)
