from authentication import validators
from mutaengine.utils import send_password_reset_email, verify_recaptcha
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    recaptcha = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'recaptcha']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken. Please choose another one.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered. Please use a different email.")
        return value

    def validate_password(self, value):
        username = self.initial_data.get('username', '')
        email = self.initial_data.get('email', '')

        return validators.validate_password(value, username, email)
    
    def validate_recaptcha(self, value):
        if not verify_recaptcha(value):
            raise ValidationError("Invalid reCAPTCHA. Please try again.")

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomTokenObtainSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    recaptcha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        recaptcha_response = attrs.pop('recaptcha', None)
        if not verify_recaptcha(recaptcha_response):
            raise ValidationError("Invalid reCAPTCHA. Please try again.")

        user = User.objects.filter(username=username_or_email).first() or \
               User.objects.filter(email=username_or_email).first()

        if user is None:
            raise NotFound('User not found.')

        user = authenticate(username=user.username, password=password)

        if user is None:
            raise AuthenticationFailed('Incorrect password.')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("No user is associated with this email address.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = int_to_base36(user.pk)
        
        reset_link = f"{settings.FRONTEND_URL}/reset-password/?token={token}&uid={uid}"
        
        send_password_reset_email(user, reset_link)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')

        try:
            user_id = int(uid, 36)
            user = User.objects.get(pk=user_id)
        except (ValueError, User.DoesNotExist):
            raise ValidationError("Invalid reset link.")
        
        if not default_token_generator.check_token(user, token):
            raise ValidationError("Invalid or expired token.")
        
        try:
            validators.validate_password(attrs.get('new_password'), user.username, user.email)
        except ValidationError as e:
            raise ValidationError({"new_password": str(e)})


        return attrs

    def save(self):
        uid = self.validated_data['uid']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user_id = int(uid, 36)
        user = User.objects.get(pk=user_id)
        user.set_password(new_password)
        user.save()
        
        
class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField()

    def validate(self, attrs):
        id_token_str = attrs.get('id_token')

        try:
            idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

            if 'email' not in idinfo or 'sub' not in idinfo:
                raise AuthenticationFailed("Invalid Google token")
            
            email = idinfo['email']

            # Get or create the user based on the email
            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
            })

            attrs['user'] = user
            attrs['created'] = created
            return attrs

        except ValueError:
            raise AuthenticationFailed("Invalid or expired Google token")

    def create(self, validated_data):
        user = validated_data['user']

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'created': validated_data['created']  # Indicate if the user was created or existed
        }