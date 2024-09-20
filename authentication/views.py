from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer, CustomTokenObtainSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, GoogleSignInSerializer
from mutaengine.utils import custom_response
from mutaengine.base_view import BaseAPIView

class RegisterUserView(BaseAPIView, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
    
    def create_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return custom_response(
                message="User registered successfully",
                data={
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                status_code=status.HTTP_201_CREATED
            )
        else:
            return custom_response(
                message="User registration failed",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.create_user, *args, **kwargs)


class CustomTokenObtainView(BaseAPIView):
    def authenticate_user(self, request, *args, **kwargs):
        serializer = CustomTokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.validated_data
            return custom_response(
                message="Login successful",
                data=tokens,
                status_code=status.HTTP_200_OK
            )
        else:
            return custom_response(
                message="Invalid credentials",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.authenticate_user, *args, **kwargs)


class PasswordResetRequestView(BaseAPIView, generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def send_password_reset_link(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                message="Password reset email sent.",
                data={},
                status_code=status.HTTP_200_OK
            )
        return custom_response(
            message="Invalid email address.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.send_password_reset_link, *args, **kwargs)
    
class PasswordResetConfirmView(BaseAPIView, generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def password_reset(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                message="Password has been reset successfully.",
                data={},
                status_code=status.HTTP_200_OK
            )
        return custom_response(
            message="Invalid token or password reset failed.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.password_reset, *args, **kwargs)
    
    
class GoogleSignInView(BaseAPIView):
    permission_classes = (AllowAny,)
    
    def google_signin(self, request, *args, **kwargs):
        serializer = GoogleSignInSerializer(data=request.data)

        if serializer.is_valid():
            # Call the create method from the serializer to get the JWT tokens and user data
            result = serializer.save()

            return custom_response(
                message="Login successful",
                data=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return custom_response(
                message="Invalid credentials",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.google_signin, *args, **kwargs)