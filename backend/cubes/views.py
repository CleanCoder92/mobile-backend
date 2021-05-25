from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from django.db.models import Count
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Q

from tiles.models import Tile, HashTags, TileFavorites, TileComment, History
from users.models import Following, User
from common.serializers import serialize_user, serialize_cube, serialize_tile, serialize_cube_comment
from common.task import cube_comment_notification, cube_favorite_notification, comment_favorite_notification, \
    subscription_notification
from .serializers import CubeCreateSerializer, CubeListSerializer, CubeUpdateSerializer, CommentCreateSerializer, \
    SubscriptionCreateSerializer, CommentFavoriteSerializer, CubeFavoriteSerializer
from .models import Cube, CubeFavorites, CubeComment, CubeCommentFavorite


class CubeCreateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CubeCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = Cube()
        cube.user = request.user
        cube.type = serializer.data.get('type')
        cube.caption = serializer.data.get('caption')
        cube.save()
        tiles = serializer.data.get('tiles')
        Tiles = []
        if tiles:
            for tile in tiles:
                til = Tile(
                    cube=cube,
                    description=tile['description'],
                    link=tile['link'],
                    sequence=tile['sequence'],
                    photo_url=tile['photo_url'],
                    thumb_url=tile['thumb_url'],
                    video_embed_code=tile['video_embed_code']
                )
                til.save()
                tags = tile['tags']
                Tags = []
                if tags:
                    for tag in tags:
                        tag = HashTags(tile=til, tag=tag)
                        tag.save()
                        Tags.append(tag.tag)
                Tiles.append({
                        **serialize_tile(til),
                        "number_of_likes": 0,
                        "number_of_comments": 0,
                        "tags": Tags,
                    })
        return Response(
            {
                "result": True,
                "data": {
                    "cube": {
                        **serialize_cube(cube),
                        "user": serialize_user(cube.user),
                        "number_of_likes": 0,
                        "number_of_comments": 0,
                        "tiles": Tiles
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class CubeListView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CubeListSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        allcubes = Cube.objects.filter(user=user).order_by('-created_at')
        page = request.GET.get('page')
        paginator = Paginator(allcubes, 5)
        cube_list = []
        try:
            cubes = paginator.page(page)
        except PageNotAnInteger:
            cubes = paginator.page(1)
        except EmptyPage:
            cubes = []

        for cube in cubes:
            favorites = CubeFavorites.objects.filter(cube=cube).count()
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()
            comments = CubeComment.objects.filter(cube=cube).count()
            tiles = Tile.objects.filter(cube=cube)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                            **serialize_tile(tile),
                            "number_of_likes": tile_favorites,
                            "number_of_comments": tile_comments,
                            "tags": Tags,
                        })
            cube_list.append({
                    **serialize_cube(cube),
                    "number_of_likes": favorites,
                    "number_of_comments": comments,
                    "is_favorite": is_favorite,
                    "user": serialize_user(cube.user),
                    "tiles": Tiles
            })
        return Response(
            {
                "result": True,
                "data": {
                    "cubes": cube_list,
                }
            },
            status=status.HTTP_201_CREATED
        )


class CubeDetailView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            cube = Cube.objects.get(id=pk)
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()
            favorites = CubeFavorites.objects.filter(cube=cube).count()
            comments = CubeComment.objects.filter(cube=cube).count()
            tiles = Tile.objects.filter(cube=cube)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                            **serialize_tile(tile),
                            "number_of_likes": tile_favorites,
                            "number_of_comments": tile_comments,
                            "tags": Tags,
                        })

            return Response(
                {
                    "result": True,
                    "data": {
                        "cube": {
                            **serialize_cube(cube),
                            "number_of_likes": favorites,
                            "number_of_comments": comments,
                            "is_favorite": is_favorite,
                            "user": serialize_user(cube.user),
                            "tiles": Tiles
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 3,
                    "errorMsg": "Cube not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            cube = Cube.objects.get(user=request.user, id=pk)
            cube.delete()
            return Response(
                {
                    "result": True,
                    "data": {
                        "msg": "Cube deleted"
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 1,
                    "errorMsg": "Cube is invalid or you can't delete this cube."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CubeCommentView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            cube = Cube.objects.get(id=pk)
            comments_count = CubeComment.objects.filter(cube=cube).count()
            allcomments = CubeComment.objects.filter(cube=cube).order_by('updated_at')
            page = request.GET.get('page')
            paginator = Paginator(allcomments, 5)

            comments_array = []
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
                comments = paginator.page(1)
            except EmptyPage:
                comments = []
            for comment in comments:
                user = comment.user
                is_favorite = CubeCommentFavorite.objects.filter(user=request.user, comment=comment).exists()
                comments_array.append({
                    "number_of_follower": Following.objects.filter(followed=user).count(),
                    "user": serialize_user(user),
                    **serialize_cube_comment(comment),
                    "is_favorite": is_favorite,
                })

            return Response(
                {
                    "result": True,
                    "data": {
                        "number_of_comments": comments_count,
                        "comments": comments_array,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 3,
                    "errorMsg": "Cube not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AllCubesView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        allcubes = Cube.objects.all().order_by('-id')
        page = request.GET.get('page')
        paginator = Paginator(allcubes, 5)
        cube_list = []
        try:
            cubes = paginator.page(page)
        except PageNotAnInteger:
            cubes = paginator.page(1)
        except EmptyPage:
            cubes = []

        for cube in cubes:
            favorites = CubeFavorites.objects.filter(cube=cube).count()
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()
            comments = CubeComment.objects.filter(cube=cube).count()
            tiles = Tile.objects.filter(cube=cube)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                        **serialize_tile(tile),
                        "number_of_likes": tile_favorites,
                        "number_of_comments": tile_comments,
                        "tags": Tags,
                    })
            cube_list.append({
                **serialize_cube(cube),
                "number_of_likes": favorites,
                "number_of_comments": comments,
                "is_favorite": is_favorite,
                "user": serialize_user(cube.user),
                "tiles": Tiles
            })

        return Response(
            {
                "result": True,
                "data": {
                    "cubes": cube_list,
                }
            },
            status=status.HTTP_201_CREATED
        )


class CubeUpdateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CubeUpdateSerializer

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        cube.user = request.user
        cube.type = serializer.data.get('type')
        if serializer.data.get('caption'):
            cube.caption = serializer.data.get('caption')
        cube.save()
        favorites = CubeFavorites.objects.filter(cube=cube).count()
        comments = CubeComment.objects.filter(cube=cube).count()
        return Response(
            {
                "result": True,
                "data": {
                    "cube": {
                        **serialize_cube(cube),
                        "user": serialize_user(cube.user),
                        "number_of_likes": favorites,
                        "number_of_comments": comments,
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class CommentCreateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CommentCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        comment = CubeComment()
        time = datetime.now()
        comment.created_at = time
        comment.updated_at = time
        comment.user = request.user
        comment.cube = cube
        comment.comment = serializer.data.get('comment')
        comment.save()

        if request.user != cube.user:
            history = History(From=request.user,
                              To=cube.user,
                              cube=cube,
                              comment=comment.id,
                              type=3)
            history.save()
            cube_comment_notification.delay(request.user, cube.user)

        return Response(
            {
                "result": True,
                "data": {
                    "comment": {
                        "user": serialize_user(request.user),
                        **serialize_cube_comment(comment)
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class CubeFavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CubeFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        is_favorited = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()

        if is_favorited:
            return Response(
                {
                    "result": True,
                    "data": {
                        "cube": {
                            "cube_id": cube.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            favorite = CubeFavorites(user=request.user, cube=cube)
            favorite.save()
            if request.user != cube.user:
                history = History(From=request.user,
                                  To=cube.user,
                                  cube=cube,
                                  type=2)
                history.save()
                cube_favorite_notification.delay(request.user, cube.user)
            return Response(
                {
                    "result": True,
                    "data": {
                        "cube": {
                            "cube_id": cube.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )


class CubeUnfavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CubeFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        is_favorited = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()

        if is_favorited:
            CubeFavorites.objects.filter(user=request.user, cube=cube).delete()
            return Response({"result": True}, status=status.HTTP_201_CREATED)
        else:
            return Response({"result": True}, status=status.HTTP_201_CREATED)


class CommentFavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CommentFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data['comment']
        is_favorited = CubeCommentFavorite.objects.filter(user=request.user, comment=comment).exists()

        if is_favorited:
            return Response(
                {
                    "result": True,
                    "data": {
                        "comment": {
                            "comment_id": comment.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            favorite = CubeCommentFavorite(user=request.user, comment=comment)
            favorite.save()
            if request.user != comment.user:
                history = History(From=request.user,
                                  To=comment.user,
                                  cube=comment.cube,
                                  comment=comment.id,
                                  type=4)
                history.save()
                comment_favorite_notification.delay(request.user, comment.user)
            return Response(
                {
                    "result": True,
                    "data": {
                        "comment": {
                            "comment_id": comment.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )


class CommentUnfavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CommentFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data['comment']
        is_favorited = CubeCommentFavorite.objects.filter(user=request.user, comment=comment).exists()

        if is_favorited:
            CubeCommentFavorite.objects.filter(user=request.user, comment=comment).delete()
            return Response({"result": True}, status=status.HTTP_201_CREATED)
        else:
            return Response({"result": True}, status=status.HTTP_201_CREATED)


class SubscriptionCreateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = SubscriptionCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data['comment_object']
        subscription = CubeComment()
        subscription.created_at = datetime.now()
        subscription.updated_at = comment.created_at + timedelta(seconds=1/1000)
        subscription.user = request.user
        subscription.parent_id = comment.id
        subscription.cube = comment.cube
        subscription.comment = serializer.data.get('comment')
        subscription.save()

        if request.user != comment.user:
            history = History(From=request.user,
                              To=comment.user,
                              cube=comment.cube,
                              comment=comment.id,
                              type=5)
            history.save()
            subscription_notification.delay(request.user, comment.user)

        return Response(
            {
                "result": True,
                "data": {
                    "comment": {
                        "user": serialize_user(request.user),
                        **serialize_cube_comment(subscription)
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class DiscoverCubesView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        me = request.user
        followed_user_id = Following.objects.filter(follower=me).values_list('followed_id', flat=True)
        users = User.objects.all().exclude(Q(id__in=followed_user_id) | Q(id=me.id))

        # allcubes = Cube.objects.filter(user__in=users). \
        #     annotate(num_favorites=Count('cubefavorites')).order_by('-num_favorites', '-updated_at')
        allcubes = Cube.objects.filter(user__in=users).order_by('-id')
        page = request.GET.get('page')
        paginator = Paginator(allcubes, 5)
        cube_list = []
        try:
            cubes = paginator.page(page)
        except PageNotAnInteger:
            cubes = paginator.page(1)
        except EmptyPage:
            cubes = []

        for cube in cubes:
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()
            favorites = CubeFavorites.objects.filter(cube=cube).count()
            comments = CubeComment.objects.filter(cube=cube).count()
            tiles = Tile.objects.filter(cube=cube)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                            **serialize_tile(tile),
                            "number_of_likes": tile_favorites,
                            "number_of_comments": tile_comments,
                            "tags": Tags,
                        })
            cube_list.append({
                    **serialize_cube(cube),
                    "number_of_likes": favorites,
                    "number_of_comments": comments,
                    "is_favorite": is_favorite,
                    "user": serialize_user(cube.user),
                    "tiles": Tiles
            })
        return Response(
            {
                "result": True,
                "data": {
                    "cubes": cube_list,
                }
            },
            status=status.HTTP_201_CREATED
        )


class FollowingCubesView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        me = request.user
        followed_user_id = Following.objects.filter(follower=me).values_list('followed_id', flat=True)
        users = User.objects.filter(id__in=followed_user_id)

        allcubes = Cube.objects.filter(user__in=users).\
            annotate(num_favorites=Count('cubefavorites')).order_by('-num_favorites')
        page = request.GET.get('page')
        paginator = Paginator(allcubes, 5)
        cube_list = []
        try:
            cubes = paginator.page(page)
        except PageNotAnInteger:
            cubes = paginator.page(1)
        except EmptyPage:
            cubes = []

        for cube in cubes:
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=cube).exists()
            favorites = CubeFavorites.objects.filter(cube=cube).count()
            comments = CubeComment.objects.filter(cube=cube).count()
            tiles = Tile.objects.filter(cube=cube)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                            **serialize_tile(tile),
                            "number_of_likes": tile_favorites,
                            "number_of_comments": tile_comments,
                            "tags": Tags,
                        })
            cube_list.append({
                    **serialize_cube(cube),
                    "number_of_likes": favorites,
                    "number_of_comments": comments,
                    "is_favorite": is_favorite,
                    "user": serialize_user(cube.user),
                    "tiles": Tiles
            })
        return Response(
            {
                "result": True,
                "data": {
                    "cubes": cube_list,
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
            allsearchcubes_id = Cube.objects.filter(Q(caption__icontains=keyword)).values_list('id', flat=True).distinct('id')
            allsearchtiles = Tile.objects.filter(Q(description__icontains=keyword)).values_list('cube_id', flat=True).distinct('cube_id')
            allsearchtags = HashTags.objects.filter(Q(tag__icontains=keyword)).values_list('tile_id', flat=True).distinct('tile_id')
            pre_cube_array = Tile.objects.filter(id__in=allsearchtags).values_list('cube_id', flat=True)
            all_cube_id = Cube.objects.filter(Q(id__in=allsearchcubes_id) | Q(id__in=allsearchtiles) | Q(id__in=pre_cube_array)).values_list('id', flat=True).distinct('id')
            allsearchcubes = Cube.objects.filter(id__in=all_cube_id).order_by('-updated_at')
            number_of_cubes = Cube.objects.filter(id__in=all_cube_id).count()
        else:
            allsearchcubes = Cube.objects.all().order_by('-updated_at')
            number_of_cubes = Cube.objects.all().count()
        paginator = Paginator(allsearchcubes, 5)
        try:
            search = paginator.page(page)
        except PageNotAnInteger:
            search = paginator.page(1)
        except EmptyPage:
            search = []

        sea_Cubes = []
        for sea in search:
            is_favorite = CubeFavorites.objects.filter(user=request.user, cube=sea).exists()
            favorites = CubeFavorites.objects.filter(cube=sea).count()
            comments = CubeComment.objects.filter(cube=sea).count()
            tiles = Tile.objects.filter(cube=sea)

            Tiles = []
            if tiles:
                for tile in tiles:
                    tile_favorites = TileFavorites.objects.filter(tile=tile).count()
                    tile_comments = TileComment.objects.filter(tile=tile).count()
                    tags = HashTags.objects.filter(tile=tile)

                    Tags = []
                    if tags:
                        for tag in tags:
                            Tags.append(tag.tag)
                    Tiles.append({
                            **serialize_tile(tile),
                            "number_of_likes": tile_favorites,
                            "number_of_comments": tile_comments,
                            "tags": Tags,
                        })
            sea_Cubes.append({
                    **serialize_cube(sea),
                    "number_of_likes": favorites,
                    "number_of_comments": comments,
                    "is_favorite": is_favorite,
                    "user": serialize_user(sea.user),
                    "tiles": Tiles
            })
        return Response(
            {
                "result": True,
                "data": {
                    "number_of_cubes": number_of_cubes,
                    "cubes": sea_Cubes,
                }
            },
            status=status.HTTP_201_CREATED
        )


class CubeReportlView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            cube = Cube.objects.get(id=pk)
            return Response(
                {
                    "result": True,
                    "data": {
                        "msg": "Cube reported successfully."
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 3,
                    "errorMsg": "Cube not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
