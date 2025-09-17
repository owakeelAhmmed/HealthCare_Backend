from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
# from knox.models import AuthToken
from .serializers import UserSerializer, LoginSerializer
from rest_framework import status
from .models import User
from .serializers import UserRegisterSerializer
from .serializers import AdminCreateUserSerializer


# Create your views here.

# Register API
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class AdminOnlyLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user and user.user_type == 3:  # Admin only
            return Response({"message": "Admin login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials or not admin"}, status=status.HTTP_401_UNAUTHORIZED)


class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminCreateUserSerializer
    permission_classes = [permissions.IsAdminUser]  # শুধু admin access


# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })