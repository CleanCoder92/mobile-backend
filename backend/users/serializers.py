from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from common.exception import CustomException

from users.models import User
from tiles.models import History


class GetUserByIdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'invalid_user': _('User not found.'),
        'empty_user_id': _('User_id is required.'),
    }

    def validate(self, attrs):
        user_id = attrs.get("user_id")

        if not user_id:
            raise CustomException(code=10, message=self.error_messages['empty_user_id'])

        try:
            attrs['user'] = User.objects.get(id=user_id)
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_user'])


class FollowingSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'invalid_user': _('User is invalid.'),
    }

    def validate(self, attrs):
        user_id = attrs.get("user_id")

        if not user_id:
            raise CustomException(code=10, message=self.error_messages['invalid_user'])

        try:
            attrs['user'] = User.objects.get(id=user_id)
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_user'])


class UserEditSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=True)
    overview = serializers.CharField(allow_blank=True)
    location = serializers.CharField(allow_blank=True)
    avatar = serializers.CharField(allow_blank=True)

    def validate(self, attrs):
        return attrs


class GetNotificationByIdSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'invalid_notification': _('Notification not found.'),
    }

    def validate(self, attrs):
        notification_id = attrs.get("notification_id")

        try:
            attrs['notification'] = History.objects.get(id=notification_id)
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_notification'])
