from authentication.views import RegisterUserView, CustomTokenObtainView, PasswordResetConfirmView, PasswordResetRequestView, GoogleSignInView, LogoutView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'authentication'

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', CustomTokenObtainView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot_password/', PasswordResetRequestView.as_view(), name='forgot_password'),
    path('reset_password/', PasswordResetConfirmView.as_view(), name='reset_password'),
    path('google/', GoogleSignInView.as_view(), name='google_login'),
]
