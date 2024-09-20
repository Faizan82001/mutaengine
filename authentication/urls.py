from authentication.views import RegisterUserView, CustomTokenObtainView, PasswordResetConfirmView, PasswordResetRequestView, GoogleSignInView
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', CustomTokenObtainView.as_view(), name='login'),
    path('forgot_password/', PasswordResetRequestView.as_view(), name='forgot_password'),
    path('reset_password/', PasswordResetConfirmView.as_view(), name='reset_password'),
    path('google/', GoogleSignInView.as_view(), name='google_login'),
]
