from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_auth.views import LoginView, LogoutView
from rest_framework.authtoken.models import Token
from fcm_django.models import FCMDevice
from datetime import datetime
import random

from users.models import User
from .serializers import RegistrationSerializer, SocialLoginSerializer, ForgotSerializer, ConfirmTokenSerializer, \
    ResetPasswordSerializer, ChangePasswordSerializer


class UserLoginView(LoginView):
    def get_response(self):
        original_response = super().get_response()

        response = {
            "result": True,
            "data": {
                "token": original_response.data.get('key'),
                "user": {
                    "user_id": self.user.id,
                    "email": self.user.email,
                    "username": self.user.username,
                }
            }
        }

        return Response(response, status=status.HTTP_201_CREATED)


class UserRegistrationView(CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response({"result": True}, status=status.HTTP_201_CREATED, headers=headers)


class SocialLoginView(CreateAPIView):
    serializer_class = SocialLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_info = serializer.validated_data['user_info']
        provider = serializer.data.get('provider')

        if provider == 'apple':
            try:
                user = User.objects.get(apple_id=user_info['uid'])
            except ObjectDoesNotExist:
                user = User()
                user.apple_id = user_info['uid']
                user.email = user_info['email'] if 'email' in user_info else None
                user.username = user_info['name'] if 'name' in user_info else None
                user.save()
        else:
            try:
                user = User.objects.get(email=user_info['email'])
            except ObjectDoesNotExist:
                user = User()
                if provider == 'google':
                    user.email = user_info['email']
                    user.username = user_info['name']
                    user.email_confirmed = True
                elif provider == 'facebook':
                    user.email = user_info['email']
                    user.username = user_info['name']
                    user.email_confirmed = True
                user.save()

        if not user.is_active:
            return Response(
                {
                    "result": False,
                    "errorCode": 13,
                    "errorMsg": "User account is disabled."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            token = Token.objects.get(user=user)
        except ObjectDoesNotExist:
            token = Token.objects.create(user=user)
        response = {
            "result": True,
            "data": {
                "token": token.key,
                "user": {
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                }
            }
        }

        return Response(response, status=status.HTTP_201_CREATED)


class UserLogoutView(LogoutView):
    def logout(self, request):
        FCMDevice.objects.filter(user=request.user).delete()
        super().logout(request)
        return Response({"result": True}, status=status.HTTP_201_CREATED)


class ForgotPasswordView(CreateAPIView):
    serializer_class = ForgotSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data.get('email')

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                token = random.randint(1000, 9999)
                user.password_reset_token = token
                user.password_reset_sent_at = datetime.now()
                user.save()
                send_mail(
                    'Please reset your password',
                    'We heard that you lost your Clout9 password. Sorry about that!\n\n\n'
                    'But don’t worry! You can use the following code to reset your password:\n\n'
                    'Code is:   ' + str(token) +
                    '\n\nIf you don’t use this code within 10 minutes, it will expire.'
                    '\n\n\n\n\nThanks\nThe Clout9 Team',
                    'admin@clout9nine.com',
                    [email]
                )
            else:
                return Response(
                    {
                        "result": False,
                        "errorCode": 10,
                        "errorMsg": "User isn't active status."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 11,
                    "errorMsg": "Can't find Email"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({"result": True}, status=status.HTTP_201_CREATED)


class ConfirmTokenView(CreateAPIView):
    serializer_class = ConfirmTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(password_reset_token=int(serializer.data.get('token')))
        user.password_reset_sent_at = None
        user.save()

        return Response({"result": True}, status=status.HTTP_201_CREATED)


class ResetPasswordView(CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(password_reset_token=int(serializer.data.get('token')))
        user.password = serializer.data.get('password')
        user.password_reset_token = None
        user.save()

        return Response({"result": True}, status=status.HTTP_201_CREATED)


class ChangePasswordView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = ChangePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'user_id': request.user.id,
            'current_password': request.data.get('current_password'),
            'new_password': request.data.get('new_password')
        })
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.password = serializer.data.get('new_password')
        user.save()

        return Response({"result": True}, status=status.HTTP_200_OK)
