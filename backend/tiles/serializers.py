from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from common.exception import CustomException
from cubes.models import Cube
from .models import Tile, TileComment


class TileCreateSerializer(serializers.ModelSerializer):
    cube_id = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    link = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sequence = serializers.IntegerField(required=False)
    photo_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    thumb_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    video_embed_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    tags = serializers.ListField(required=False)

    default_error_messages = {
        'invalid_cube': _('Cube is invalid.'),
        'invalid_sequence': _('sequence is Empty.'),
    }

    class Meta:
        model = Tile
        fields = ("cube_id", "description", "link", "sequence", "photo_url", "thumb_url", "video_embed_code", "tags")

    def validate(self, attrs):
        cube_id = attrs.get("cube_id")
        sequence = attrs.get("sequence")

        if not cube_id:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])
        if not sequence:
            raise CustomException(code=13, message=self.error_messages['invalid_sequence'])
        try:
            cube = Cube.objects.get(id=cube_id)
            attrs['cube'] = cube
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])


class TileUpdateSerializer(serializers.ModelSerializer):
    cube_id = serializers.IntegerField(required=False)
    tile_id = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    link = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sequence = serializers.IntegerField(required=False)
    photo_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    thumb_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    video_embed_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    tags = serializers.ListField(required=False)

    default_error_messages = {
        'invalid_cube': _('Cube is invalid.'),
        'invalid_tile': _('Tile is invalid.'),
        'invalid_sequence': _('sequence is Empty.'),
    }

    class Meta:
        model = Tile
        fields = ("cube_id", "tile_id", "description", "link", "sequence", "photo_url", "thumb_url", "video_embed_code"
                  , "tags")

    def validate(self, attrs):
        cube_id = attrs.get("cube_id")
        tile_id = attrs.get("tile_id")
        sequence = attrs.get("sequence")

        if not cube_id:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])
        if not tile_id:
            raise CustomException(code=11, message=self.error_messages['invalid_tile'])
        if not sequence:
            raise CustomException(code=14, message=self.error_messages['invalid_sequence'])
        try:
            cube = Cube.objects.get(id=cube_id)
            tile = Tile.objects.get(id=tile_id, cube=cube)
            attrs['cube'] = cube
            attrs['tile'] = tile
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_cube'])


class CommentCreateSerializer(serializers.ModelSerializer):
    tile_id = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False)

    default_error_messages = {
        'invalid_tile': _('Tile is invalid.'),
        'invalid_comment': _('Comment is invalid.'),
    }

    class Meta:
        model = Tile
        fields = ("tile_id", "comment")

    def validate(self, attrs):
        tile_id = attrs.get("tile_id")
        comment = attrs.get("comment")

        if not tile_id:
            raise CustomException(code=10, message=self.error_messages['invalid_tile'])
        if not comment:
            raise CustomException(code=11, message=self.error_messages['invalid_comment'])
        try:
            tile = Tile.objects.get(id=tile_id)
            attrs['tile'] = tile
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_tile'])


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
            comment = TileComment.objects.get(id=comment_id)
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
            comment_object = TileComment.objects.get(id=parent_id, parent_id=None)
            attrs['comment_object'] = comment_object
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=10, message=self.error_messages['invalid_parent'])


class TileFavoriteSerializer(serializers.ModelSerializer):
    tile_id = serializers.IntegerField(required=False)

    default_error_messages = {
        'empty_tile': _('Tile_id is Empty.'),
        'invalid_tile': _('Tile_id is Invalid.'),
    }

    class Meta:
        model = Tile
        fields = ("tile_id",)

    def validate(self, attrs):
        tile_id = attrs.get("tile_id")

        if not tile_id:
            raise CustomException(code=10, message=self.error_messages['empty_tile'])
        try:
            tile = Tile.objects.get(id=tile_id)
            attrs['tile'] = tile
            return attrs
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_tile'])
