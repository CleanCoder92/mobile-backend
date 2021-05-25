from django.urls import path, re_path, include

from .views import UserLoginView, UserRegistrationView, UserLogoutView, SocialLoginView, ForgotPasswordView, \
    ConfirmTokenView, ResetPasswordView, ChangePasswordView

app_name = 'api'

urlpatterns = [
    path('login/', UserLoginView.as_view()),
    path('register/', UserRegistrationView.as_view()),
    path('social-login/', SocialLoginView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('confirm-token/', ConfirmTokenView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    re_path(r'^users/', include('users.urls')),
    re_path(r'^cubes/', include('cubes.urls')),
    re_path(r'^tiles/', include('tiles.urls')),
]
