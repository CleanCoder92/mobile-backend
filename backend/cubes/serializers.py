from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from common.exception import CustomException
from users.models import User
from .models import Cube, CubeComment


class CubeCreateSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False)
    caption = serializers.CharField(allow_blank=True)
    tiles = serializers.ListField(required=False)

    default_error_messages = {
        'invalid_type': _('type is invalid.'),
    }

    class Meta:
        model = Cube
        fields = ("type", "caption", "tiles")

    def validate(self, attrs):
        cube_type = attrs.get("type")

        if not cube_type:
            raise CustomException(code=10, message=self.error_messages['invalid_type'])

        return attrs


class CubeListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'empty_user': _('user_id is Empty.'),
        'invalid_user': _('user_id is invalid.'),
    }

    class Meta:
        model = User
        fields = ("user_id",)

    def validate(self, attrs):
        user_id = attrs.get("user_id")

        if not user_id:
            raise CustomException(code=10, message=self.error_messages['empty_user'])

        try:
            attrs['user'] = User.objects.get(id=user_id)
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_user'])


class CubeUpdateSerializer(serializers.ModelSerializer):
    cube_id = serializers.IntegerField(required=False)
    type = serializers.IntegerField(required=False)
    caption = serializers.CharField(allow_null=True, allow_blank=True)

    default_error_messages = {
        'invalid_cube': _('Cube is invalid.'),
        'invalid_type': _('type is invalid.'),
    }

    class Meta:
        model = Cube
        fields = ("cube_id", "type", "caption")

    def validate(self, attrs):
        cube_id = attrs.get("cube_id")
        cube_type = attrs.get("type")

        if not cube_id:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])
        if not cube_type:
            raise CustomException(code=11, message=self.error_messages['invalid_type'])
        try:
            cube = Cube.objects.get(id=cube_id)
            attrs['cube'] = cube
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])


class CommentCreateSerializer(serializers.ModelSerializer):
    cube_id = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_cube': _('Cube is invalid.'),
        'invalid_comment': _('Comment is invalid.'),
    }

    class Meta:
        model = Cube
        fields = ("cube_id", "comment")

    def validate(self, attrs):
        cube_id = attrs.get("cube_id")
        comment = attrs.get("comment")

        if not cube_id:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])
        if not comment:
            raise CustomException(code=11, message=self.error_messages['invalid_comment'])
        try:
            cube = Cube.objects.get(id=cube_id)
            attrs['cube'] = cube
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])


class CommentFavoriteSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'empty_comment': _('Comment_id is Empty.'),
        'invalid_comment': _('Comment_id is Invalid.'),
    }

    class Meta:
        model = Cube
        fields = ("comment_id",)

    def validate(self, attrs):
        comment_id = attrs.get("comment_id")

        if not comment_id:
            raise CustomException(code=10, message=self.error_messages['empty_comment'])
        try:
            comment = CubeComment.objects.get(id=comment_id)
            attrs['comment'] = comment
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_comment'])


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_parent': _('Parent comment is invalid.'),
        'invalid_comment': _('comment is Empty.'),
    }

    class Meta:
        model = Cube
        fields = ("parent_id", "comment")

    def validate(self, attrs):
        parent_id = attrs.get("parent_id")
        comment = attrs.get("comment")

        if not parent_id:
            raise CustomException(code=10, message=self.error_messages['invalid_parent'])
        if not comment:
            raise CustomException(code=11, message=self.error_messages['invalid_comment'])
        try:
            comment_object = CubeComment.objects.get(id=parent_id, parent_id=None)
            attrs['comment_object'] = comment_object
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_parent'])


class CubeFavoriteSerializer(serializers.ModelSerializer):
    cube_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'empty_cube': _('Cube_id is Empty.'),
        'invalid_cube': _('Cube_id is Invalid.'),
    }

    class Meta:
        model = Cube
        fields = ("cube_id",)

    def validate(self, attrs):
        cube_id = attrs.get("cube_id")

        if not cube_id:
            raise CustomException(code=10, message=self.error_messages['empty_cube'])
        try:
            cube = Cube.objects.get(id=cube_id)
            attrs['cube'] = cube
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_cube'])
