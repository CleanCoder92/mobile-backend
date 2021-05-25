from fcm_django.models import FCMDevice


def serialize_user(user):
    return {
        "user_id": user.id,
        "username": user.username,
        "createdAt": user.date_joined,
        "updatedAt": user.date_joined,
        "avatar": user.avatar
    }


def serialize_cube(cube):
    return {
        "cube_id": cube.id,
        "type": cube.type,
        "caption": cube.caption,
        "createdAt": cube.created_at,
        "updatedAt": cube.updated_at
    }


def serialize_cube_comment(comment):
    if comment.parent_id:
        parent_id = comment.parent_id
    else:
        parent_id = 0
    return {
        "comment_id": comment.id,
        "parent_id": parent_id,
        "cube_id": comment.cube.id,
        "comment": comment.comment,
        "createdAt": comment.created_at
    }


def serialize_tile(tile):
    return {
        "tile_id": tile.id,
        "description": tile.description,
        "link": tile.link,
        "photo_url": tile.photo_url,
        "thumb_url": tile.thumb_url,
        "video_embed_code": tile.video_embed_code,
        "sequence": tile.sequence,
        "createdAt": tile.created_at,
        "updatedAt": tile.updated_at
    }


def serialize_tile_comment(comment):
    if comment.parent_id:
        parent_id = comment.parent_id
    else:
        parent_id = 0
    return {
        "comment_id": comment.id,
        "parent_id": parent_id,
        "tile_id": comment.tile.id,
        "comment": comment.comment,
        "createdAt": comment.created_at
    }


def serialize_notification(notification):
    if not notification.cube:
        cube_id = None
    else:
        cube_id = notification.cube.id
    if not notification.tile:
        tile_id = None
    else:
        tile_id = notification.tile.id
    return {
        "id": notification.id,
        "created_at": notification.created_at,
        "type": notification.type,
        "new_notification": notification.new_notification,
        "cube_id": cube_id,
        "tile_id": tile_id,
        "comment_id": notification.comment
    }


def follow_notification(follower, followed):
    devices = FCMDevice.objects.filter(user=followed)
    if devices:
        for device in devices:
            device.send_message(title="Following", body=follower.username + " followed You")


def tile_comment_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Tile Comment", body=commenter.username + " commented Your Tile")


def tile_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Tile Favorite", body=commenter.username + " favorite Your Tile")


def cube_comment_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Cube Comment", body=commenter.username + " commented Your Cube")


def cube_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Cube Favorite", body=commenter.username + " favorite Your Cube")


def comment_favorite_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Comment Favorite", body=commenter.username + " favorite Your comment")


def subscription_notification(commenter, to):
    devices = FCMDevice.objects.filter(user=to)
    if devices:
        for device in devices:
            device.send_message(title="Comment", body=commenter.username + " commented Your comment")
