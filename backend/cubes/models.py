from django.db import models
from users.models import User
from common.models import BaseModel


class Category(models.Model):
    name = models.CharField(blank=False, max_length=255)

    def __str__(self):
        return self.name


class Cube(BaseModel):
    class Meta:
        db_table = 'cube'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField(null=True)
    caption = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.pk


class CubeFavorites(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE)

    def __str__(self):
        return self.pk


class CubeComment(models.Model):

    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('cubes.CubeComment', on_delete=models.CASCADE, null=True)
    cube = models.ForeignKey(Cube, on_delete=models.CASCADE)
    comment = models.TextField(null=True)

    def __str__(self):
        return self.pk


class CubeCommentFavorite(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(CubeComment, on_delete=models.CASCADE)

    def __str__(self):
        return self.pk
