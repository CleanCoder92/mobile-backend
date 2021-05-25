import re
import requests
import jwt
from datetime import datetime, timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.utils import json

from common.exception import CustomException
from users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    default_error_messages = {
        'duplicate_Email': _('Duplicate Email.'),
        'invalid_email': _('Email is invalid or already taken.'),
        'invalid_username': _('Username is invalid.'),
        'invalid_password': _('Password must have at least 6 characters.'),
    }

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        password = attrs.get("password")
        email_re = '^[_aA-zZ0-9-]+(\.[_aA-zZ0-9-]+)*@[aA-zZ0-9-]+(\.[aA-zZ0-9-]+)*(\.[aA-zZ]{2,4})$'

        if not email or not bool(re.match(email_re, email)):
            raise CustomException(code=11, message=self.error_messages['invalid_email'])
        if User.objects.filter(email=email).exists():
            raise CustomException(code=10, message=self.error_messages['duplicate_Email'])
        if not username:
            raise CustomException(code=12, message=self.error_messages['invalid_username'])
        if not password or len(password) < 6:
            raise CustomException(code=13, message=self.error_messages['invalid_password'])

        attrs['password'] = make_password(attrs['password'])
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_email': _('email is required.'),
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Unable to login with provided credentials.')
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if not email:
            raise CustomException(code=10, message=self.error_messages['invalid_email'])

        try:
            self.user = get_user_model().objects.get(email=email)
            if not self.user.password:
                raise CustomException(code=11, message=self.error_messages['invalid_credentials'])
            elif self.user.check_password(password):
                if self.user.is_active:
                    attrs['user'] = self.user
                    return attrs
                else:
                    raise CustomException(code=12, message=self.error_messages['inactive_account'])
        except User.DoesNotExist:
            pass
        raise CustomException(code=11, message=self.error_messages['invalid_credentials'])


class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False)
    provider = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_token': _('Access Token is invalid.'),
        'invalid_provider': _('Google or Facebook login is supported.'),
        'wrong_token': _('wrong google token / this google token is already expired.'),
        'wrong_facebook_token': _('wrong facebook token / this facebook token is already expired.'),
        'wrong_apple_token': _('wrong apple token / this apple token is already expired.')
    }

    def validate(self, attrs):
        access_token = attrs.get("access_token")
        provider = attrs.get("provider")

        if not access_token:
            raise CustomException(code=10, message=self.error_messages['invalid_token'])
        if provider not in ["google", "facebook", "apple"]:
            raise CustomException(code=11, message=self.error_messages['invalid_provider'])

        if provider == "google":
            payload = {'access_token': access_token}  # validate the token
            r = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', params=payload)
            data = json.loads(r.text)

            if 'error' in data:
                raise CustomException(code=12, message=self.error_messages['wrong_token'])

            attrs['user_info'] = data
        elif provider == "facebook":
            payload = {'access_token': access_token}  # validate the token
            r = requests.get('https://graph.facebook.com/me?fields=email,name', params=payload)
            data = json.loads(r.text)

            if 'error' in data:
                raise CustomException(code=13, message=self.error_messages['wrong_facebook_token'])

            attrs['user_info'] = data
        elif provider == "apple":
            headers = {
                'kid': 'HM6N2ZC42D'
            }

            client_id = 'com.cloud9.Clout-9'
            payload = {
                'iss': 'PYY8YCXYS3',
                'iat': timezone.now(),
                'exp': timezone.now() + timedelta(days=180),
                'aud': 'https://appleid.apple.com',
                'sub': client_id,
            }

            client_secret = jwt.encode(
                payload,
                '-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgZLxy1b7Qb6j31IKa\nFcPrPpf2I5kHh9XqNHfzNeofo6ugCgYIKoZIzj0DAQehRANCAATOq0lQFIpqFnBe\n/dvHcMZ65q3Opu+V8s41jE7qPFEVFBvPhu4zJFlJSA5CNkTnqSifDthqsbCMhXMQ\nK3sPWdZD\n-----END PRIVATE KEY-----',
                algorithm='ES256',
                headers=headers
            ).decode("utf-8")
            # print(client_secret)

            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': access_token,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://example-app.com/redirect'
            }
            print(access_token)

            res = requests.post("https://appleid.apple.com/auth/token", data=data, headers={'content-type': "application/x-www-form-urlencoded"})
            response_dict = res.json()
            id_token = response_dict.get('id_token')
            print(response_dict)
            response_data = {}

            if id_token:
                decoded = jwt.decode(id_token, '', verify=False)
                response_data.update({'email': decoded['email']}) if 'email' in decoded else None
                response_data.update({'name': decoded['name']}) if 'name' in decoded else None
                response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None
                attrs['user_info'] = response_data
            else:
                raise CustomException(code=14, message=self.error_messages['wrong_apple_token'])

        return attrs


class ForgotSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_email': _('Email is required.'),
    }

    def validate(self, attrs):
        email = attrs.get("email")
        if not email:
            raise CustomException(code=10, message=self.error_messages['invalid_email'])

        return attrs


class ConfirmTokenSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    token = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_token': _('Token is invalid.'),
        'invalid_email': _('Email is required.'),
        'token_expired': _('Reset Token has been expired.'),
        'inactive_account': _('User account is disabled.'),
    }

    def validate(self, attrs):
        email = attrs.get("email")
        token = attrs.get("token")
        if not email:
            raise CustomException(code=10, message=self.error_messages['invalid_email'])
        if not token or not token.isdigit():
            raise CustomException(code=11, message=self.error_messages['invalid_token'])

        try:
            user = User.objects.get(email=email, password_reset_token=int(token))
            if not user.is_active:
                raise CustomException(code=12, message=self.error_messages['inactive_account'])
            if user.password_reset_sent_at.replace(tzinfo=None) < datetime.now() - timedelta(minutes=10):
                raise CustomException(code=13, message=self.error_messages['token_expired'])

            return attrs
        except User.DoesNotExist:
            pass
        raise CustomException(code=11, message=self.error_messages['invalid_token'])


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_token': _('Token is invalid.'),
        'inactive_account': _('User account is disabled.'),
        'invalid_password': _('Password must have at least 6 characters.'),
    }

    def validate(self, attrs):
        token = attrs.get("token")
        password = attrs.get("password")
        if not token or not token.isdigit():
            raise CustomException(code=10, message=self.error_messages['invalid_token'])
        if not password or len(password) < 6:
            raise CustomException(code=11, message=self.error_messages['invalid_password'])

        try:
            user = User.objects.get(password_reset_token=int(token))
            if user.password_reset_sent_at:
                raise CustomException(code=10, message=self.error_messages['invalid_token'])
            if not user.is_active:
                raise CustomException(code=12, message=self.error_messages['inactive_account'])

            attrs['password'] = make_password(attrs['password'])
            return attrs
        except User.DoesNotExist:
            pass
        raise CustomException(code=10, message=self.error_messages['invalid_token'])


class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    current_password = serializers.CharField(allow_blank=True, allow_null=True)
    new_password = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_current_password': _('Current_password is incorrect.'),
        'invalid_password': _('Password must have at least 6 characters.'),
        'invalid_user': _('User is invalid'),
    }

    def validate(self, attrs):
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        user_id = attrs.get("user_id")
        print(user_id)

        # if not current_password:
        #     raise CustomException(code=10, message=self.error_messages['invalid_current_password'])
        if not new_password or len(new_password) < 6:
            raise CustomException(code=11, message=self.error_messages['invalid_password'])

        user = User.objects.get(pk=user_id)

        if user.password is None:
            attrs['new_password'] = make_password(attrs['new_password'])
            return attrs
        else:
            if user.check_password(current_password):
                attrs['new_password'] = make_password(attrs['new_password'])
                return attrs
            else:
                raise CustomException(code=10, message=self.error_messages['invalid_current_password'])
