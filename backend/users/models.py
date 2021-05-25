from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(blank=True, max_length=255, unique=True)
    apple_id = models.CharField(null=True, max_length=255)
    username = models.CharField(null=True, max_length=255)
    password = models.CharField(null=True, max_length=128)
    email_confirmed = models.BooleanField(blank=False, default=False)
    overview = models.TextField(null=True)
    location = models.CharField(null=True, max_length=128)
    avatar = models.TextField(null=True)
    password_reset_token = models.IntegerField(null=True)
    password_reset_sent_at = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Following(models.Model):
    class Meta:
        db_table = 'following'

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')

    def __str__(self):
        return self.pk

