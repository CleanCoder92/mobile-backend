from django.db import models
from users.models import User
from cubes.models import Cube
from common.models import BaseModel


class Tile(BaseModel):
    class Meta:
        db_table = 'tile'
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    link = models.TextField(null=True, max_length=255)
    sequence = models.IntegerField(null=True)
    photo_url = models.TextField(null=True, max_length=255)
    thumb_url = models.TextField(null=True, max_length=255)
    video_embed_code = models.TextField(null=True, max_length=255)

    def __str__(self):
        return self.pk


class TileFavorites(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tile_like')
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)

    def __str__(self):
        return self.pk


class HashTags(BaseModel):
    class Meta:
        db_table = 'tile-hashtags'
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    tag = models.CharField(blank=False, max_length=255)

    def __str__(self):
        return self.pk


class TileComment(models.Model):

    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tile_comment')
    parent = models.ForeignKey('tiles.TileComment', on_delete=models.CASCADE, null=True)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    comment = models.TextField(null=True)

    def __str__(self):
        return self.pk


class TileCommentFavorite(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(TileComment, on_delete=models.CASCADE)

    def __str__(self):
        return self.pk


class History(BaseModel):
    class Meta:
        db_table = 'history'
    From = models.ForeignKey(User, on_delete=models.CASCADE, null=True,  related_name='from+')
    To = models.ForeignKey(User, on_delete=models.CASCADE, null=True,  related_name='to+')
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE, null=True)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE, null=True)
    comment = models.CharField(null=True, max_length=255)
    new_notification = models.BooleanField(null=True, default=True)
    type = models.IntegerField(blank=False)

    def __str__(self):
        return self.pk
