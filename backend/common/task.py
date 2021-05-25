from celery.decorators import task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
from fcm_django.models import FCMDevice


logger = get_task_logger(__name__)


@task()
def follow_notification(follower, followed):
    devices = FCMDevice.objects.filter(user=followed)
    if devices:
        for device in devices:
            device.send_message(title="Following", body=follower.username + " followed You")

@task()
def tile_comment_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Tile Comment", body=commenter.username + " commented Your Tile")

@task()
def tile_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Tile Favorite", body=commenter.username + " favorite Your Tile")

@task()
def cube_comment_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Cube Comment", body=commenter.username + " commented Your Cube")

@task()
def cube_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Cube Favorite", body=commenter.username + " favorite Your Cube")

@task()
def comment_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Comment Favorite", body=commenter.username + " favorite Your comment")

@task()
def subscription_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Comment", body=commenter.username + " commented Your comment")

@task()
def send_email(token, email):
    send_mail(
        'Your password reset token here.',
        str(token),
        'no-reply@clout9nine.com',
        [email],
        fail_silently=False
    )
