from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import GenericAPIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from fcm_django.models import FCMDevice

from cubes.models import Cube
from common.task import follow_notification
from common.serializers import serialize_user, serialize_notification
from .models import User, Following
from .serializers import GetUserByIdSerializer, FollowingSerializer, UserEditSerializer, GetNotificationByIdSerializer
from tiles.models import History


class UserDetailView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = GetUserByIdSerializer

    def get(self, request, pk):
        serializer = self.get_serializer(data={"user_id": pk})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user == request.user:
            email = user.email
            overview = user.overview
            location = user.location
            cubes_count = Cube.objects.filter(user=user).count()
            followers = Following.objects.filter(followed=user).count()
            following = Following.objects.filter(follower=user).count()

            return Response(
                {
                    "result": True,
                    "data": {
                        "user": {
                            **serialize_user(user),
                            "email": email,
                            "overview": overview,
                            "location": location,
                            "number_of_cubes": cubes_count,
                            "number_of_followers": followers,
                            "number_of_following": following
                        }
                    },
                },
                status=status.HTTP_201_CREATED
            )
        else:
            overview = user.overview
            location = user.location
            is_follow = Following.objects.filter(follower=request.user, followed=user).exists()
            cubes_count = Cube.objects.filter(user=user).count()
            followers = Following.objects.filter(followed=user).count()
            following = Following.objects.filter(follower=user).count()

            return Response(
                {
                    "result": True,
                    "data": {
                        "user": {
                            **serialize_user(user),
                            "overview": overview,
                            "number_of_cubes": cubes_count,
                            "number_of_followers": followers,
                            "number_of_following": following,
                            "location": location,
                            "is_follow": is_follow
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )


class UserProfileEditView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = UserEditSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.username = serializer.data.get('username')
        user.overview = serializer.data.get('overview')
        user.location = serializer.data.get('location')
        user.avatar = serializer.data.get('avatar')
        user.save()

        return Response(
            {
                "result": True,
                "data": {
                    "user": {
                        **serialize_user(user),
                        "email": user.email,
                        "overview": user.overview,
                        "location": user.location
                    }
                },
            },
            status=status.HTTP_201_CREATED
        )


class FollowView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = FollowingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user == request.user:
            return Response(
                {
                    "result": False,
                    "errorCode": 1,
                    "errorMsg": "You can't follow yourself"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        is_followed = Following.objects.filter(follower=request.user, followed=user).exists()

        if is_followed:
            return Response(
                {
                    "result": True,
                    "data": {
                        "follower": request.user.id,
                        "followed": user.id
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            follow = Following(follower=request.user, followed=user)
            follow.save()
            history = History(From=request.user,
                              To=user,
                              type=1)
            history.save()
            follow_notification.delay(request.user, user)
            return Response(
                {
                    "result": True,
                    "data": {
                        "follower": request.user.id,
                        "followed": user.id
                    }
                },
                status=status.HTTP_201_CREATED
            )


class UnFollowView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = FollowingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user == request.user:
            return Response(
                {
                    "result": False,
                    "errorCode": 1,
                    "errorMsg": "You can't unfollow yourself"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        is_followed = Following.objects.filter(follower=request.user, followed=user).exists()

        if is_followed:
            Following.objects.filter(follower=request.user, followed=user).delete()
            return Response(
                {
                    "result": True,
                    "data": {
                        "unfollower": request.user.id,
                        "unfollowed": user.id
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "result": True,
                    "data": {
                        "unfollower": request.user.id,
                        "unfollowed": user.id
                    }
                },
                status=status.HTTP_201_CREATED
            )


class GetFollowersView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = GetUserByIdSerializer

    def get(self, request, pk):
        serializer = self.get_serializer(data={"user_id": pk})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        followers = Following.objects.filter(followed=user)

        follower_list = []
        for follower in followers:
            cubes_count = Cube.objects.filter(user=follower.follower).count()
            follower_list.append({
                **serialize_user(follower.follower),
                "number_of_cubes": cubes_count
            })
        return Response(
            {
                "result": True,
                "data": {
                    "users": follower_list
                }
            },
            status=status.HTTP_201_CREATED
        )


class GetFollowingView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = GetUserByIdSerializer

    def get(self, request, pk):
        serializer = self.get_serializer(data={"user_id": pk})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        followings = Following.objects.filter(follower=user)

        following_list = []
        for following in followings:
            cubes_count = Cube.objects.filter(user=following.followed).count()
            following_list.append({
                **serialize_user(following.followed),
                "number_of_cubes": cubes_count
            })
        return Response(
            {
                "result": True,
                "data": {
                    "users": following_list
                }
            },
            status=status.HTTP_201_CREATED
        )


class SearchDetailView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        keyword = request.GET.get('keyword')
        page = request.GET.get('page')
        if keyword:
            allusers = User.objects.filter(username__icontains=keyword)
            number_of_users = User.objects.filter(username__icontains=keyword).count()
        else:
            allusers = User.objects.all()
            number_of_users = User.objects.all().count()
        paginator = Paginator(allusers, 10)
        try:
            search = paginator.page(page)
        except PageNotAnInteger:
            search = paginator.page(1)
        except EmptyPage:
            search = []

        sea_users = []
        for sea in search:
            cubes_count = Cube.objects.filter(user=sea).count()
            sea_users.append({
                **serialize_user(sea),
                "number_of_cubes": cubes_count
            })
        return Response(
            {
                "result": True,
                "data": {
                    "number_of_users": number_of_users,
                    "users": sea_users
                }
            },
            status=status.HTTP_201_CREATED
        )


class NotificationListView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = request.user
        notification_array = []
        if History.objects.filter(To=user).exists():
            notifications = History.objects.filter(To=user).order_by('-id')
            for notification in notifications:
                notification_array.append({
                    **serialize_notification(notification),
                    "user": serialize_user(notification.From)
                })
        return Response(
            {
                "result": True,
                "data": {
                    "notifications": notification_array
                }
            },
            status=status.HTTP_201_CREATED
        )


class NotificationCountView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = request.user
        number_of_notification = History.objects.filter(To=user, new_notification=True).count()
        return Response(
            {
                "result": True,
                "data": {
                    "number_of_notification": number_of_notification
                }
            },
            status=status.HTTP_201_CREATED
        )


class NotificationView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = GetNotificationByIdSerializer

    def get(self, request, pk):
        user = request.user
        serializer = self.get_serializer(data={"notification_id": pk})
        serializer.is_valid(raise_exception=True)
        notification = serializer.validated_data['notification']
        notification.new_notification = False
        notification.save()
        number_of_notification = History.objects.filter(To=user, new_notification=True).count()
        return Response(
            {
                "result": True,
                "data": {
                    "number_of_notification": number_of_notification
                }
            },
            status=status.HTTP_201_CREATED
        )


class UserReportView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            return Response(
                {
                    "result": True,
                    "data": {
                        "msg": "User reported successfully."
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 3,
                    "errorMsg": "User not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FCMToken(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        registration_id = request.GET.get('registration_id')
        device = FCMDevice.objects.filter(registration_id=registration_id)
        if device:
            device.delete()
        else:
            user = request.user
            device = FCMDevice()
            device.user = user
            device.registration_id = registration_id
            device.save()
            return Response({"result": True}, status=status.HTTP_201_CREATED)


class RemoveMeView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def post(self, request):
        user = request.user
        user.delete()
        return Response(
            {
                "result": True,
                "msg": "removed me successfully."
            }, status=status.HTTP_200_OK
        )
