from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Q

from users.models import Following
from .models import Tile, TileComment, TileFavorites, HashTags, TileCommentFavorite, History
from .serializers import TileCreateSerializer, TileUpdateSerializer, CommentCreateSerializer, \
    SubscriptionCreateSerializer, CommentFavoriteSerializer, TileFavoriteSerializer
from cubes.models import Cube, CubeFavorites, CubeComment
from common.task import tile_comment_notification, tile_favorite_notification, comment_favorite_notification, \
    subscription_notification
from common.serializers import serialize_tile, serialize_user, serialize_cube, serialize_tile_comment


class TileCreateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = TileCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        tile = Tile()
        tile.cube = cube
        tile.description = serializer.data.get('description')
        tile.link = serializer.data.get('link')
        tile.sequence = serializer.data.get('sequence')
        tile.photo_url = serializer.data.get('photo_url')
        tile.thumb_url = serializer.data.get('thumb_url')
        tile.video_embed_code = serializer.data.get('video_embed_code')
        tile.save()

        tags = serializer.data.get('tags')
        Tags = []
        if tags:
            for til in tags:
                tag = HashTags(tile=tile, tag=til)
                tag.save()
                Tags.append(tag.tag)
        return Response(
            {
                "result": True,
                "data": {
                    "tile": {
                        **serialize_tile(tile),
                        "tags": Tags,
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class TileDetailView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            tile = Tile.objects.get(id=pk)
            user = tile.cube.user
            is_favorite = TileFavorites.objects.filter(user=request.user, tile=tile).exists()
            favorites = TileFavorites.objects.filter(tile=tile).count()
            comments = TileComment.objects.filter(tile=tile).count()

            return Response(
                {
                    "result": True,
                    "data": {
                        "tile": {
                            **serialize_tile(tile),
                            "number_of_likes": favorites,
                            "number_of_comments": comments,
                            "is_favorite": is_favorite,
                            "user": serialize_user(user)
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
                    "errorMsg": "Tile not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            tile = Tile.objects.get(id=pk)
            tile.delete()
            return Response(
                {
                    "result": True,
                    "data": {
                        "msg": "Tile deleted"
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorCode": 1,
                    "errorMsg": "Tile is invalid."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TileCommentView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, pk):
        try:
            tile = Tile.objects.get(id=pk)
            comments_count = TileComment.objects.filter(tile=tile).count()
            allcomments = TileComment.objects.filter(tile=tile).order_by('updated_at')
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
                is_favorite = TileFavorites.objects.filter(user=user, tile=tile).exists()
                comments_array.append({
                    "number_of_follower": Following.objects.filter(followed=user).count(),
                    "user": serialize_user(user),
                    **serialize_tile_comment(comment),
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
                    "errorMsg": "Tile not found."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TileUpdateView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = TileUpdateSerializer

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cube = serializer.validated_data['cube']
        tile = serializer.validated_data['tile']
        tile.cube = cube
        tile.description = serializer.data.get('description')
        tile.link = serializer.data.get('link')
        tile.sequence = serializer.data.get('sequence')
        tile.photo_url = serializer.data.get('photo_url')
        tile.thumb_url = serializer.data.get('thumb_url')
        tile.video_embed_code = serializer.data.get('video_embed_code')
        tile.save()

        tags = serializer.data.get('tags')
        Tags = []
        if tags:
            for til in tags:
                tag = HashTags(tile=tile, tag=til)
                tag.save()
                Tags.append(tag.tag)
        return Response(
            {
                "result": True,
                "data": {
                    "tile": {
                        **serialize_tile(tile),
                        "tags": Tags,
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
        tile = serializer.validated_data['tile']
        comment = TileComment()
        time = datetime.now()
        comment.created_at = time
        comment.updated_at = time
        comment.user = request.user
        comment.tile = tile
        comment.comment = serializer.data.get('comment')
        comment.save()
        if request.user != tile.cube.user:
            history = History(From=request.user,
                              To=tile.cube.user,
                              tile=tile,
                              cube=tile.cube,
                              comment=comment.id,
                              type=6)
            history.save()
            tile_comment_notification.delay(request.user, tile.cube.user)

        return Response(
            {
                "result": True,
                "data": {
                    "comment": {
                        "user": serialize_user(request.user),
                        **serialize_tile_comment(comment)
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )


class CommentFavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = CommentFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data['comment']
        is_favorited = TileCommentFavorite.objects.filter(user=request.user, comment=comment).exists()

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
            favorite = TileCommentFavorite(user=request.user, comment=comment)
            favorite.save()
            if request.user != comment.user:
                history = History(From=request.user,
                                  To=comment.user,
                                  tile=comment.tile,
                                  cube=comment.tile.cube,
                                  comment=comment.id,
                                  type=7)
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
        is_favorited = TileCommentFavorite.objects.filter(user=request.user, comment=comment).exists()

        if is_favorited:
            TileCommentFavorite.objects.filter(user=request.user, comment=comment).delete()
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
        subscription = TileComment()
        subscription.created_at = datetime.now()
        subscription.updated_at = comment.created_at + timedelta(seconds=1/1000)
        subscription.user = request.user
        subscription.parent_id = comment.id
        subscription.tile = comment.tile
        subscription.comment = serializer.data.get('comment')
        subscription.save()

        if request.user != comment.user:
            history = History(From=request.user,
                              To=comment.user,
                              tile=comment.tile,
                              cube=comment.tile.cube,
                              comment=comment.id,
                              type=8)
            history.save()
            subscription_notification.delay(request.user, comment.user)

        return Response(
            {
                "result": True,
                "data": {
                    "comment": {
                        "user": serialize_user(request.user),
                        **serialize_tile_comment(subscription)
                    }
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
            allsearch = HashTags.objects.filter(Q(tag__icontains=keyword)).distinct('tag')
            number_of_tags = HashTags.objects.filter(Q(tag__icontains=keyword)).distinct('tag').count()
        else:
            allsearch = HashTags.objects.all().distinct('tag')
            number_of_tags = HashTags.objects.all().distinct('tag').count()
        paginator = Paginator(allsearch, 10)
        try:
            search = paginator.page(page)
        except PageNotAnInteger:
            search = paginator.page(1)
        except EmptyPage:
            search = []

        sea_Tags = []
        for sea in search:
            sea_Tags.append(sea.tag)
        return Response(
            {
                "result": True,
                "data": {
                    "number_of_tags": number_of_tags,
                    "tags": sea_Tags,
                }
            },
            status=status.HTTP_201_CREATED
        )


class SearchTagDetailView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        keyword = request.GET.get('keyword')
        page = request.GET.get('page')
        if keyword:
            allsearchtags = HashTags.objects.filter(tag__icontains=keyword).values_list('tile_id', flat=True).distinct('tile_id')
            pre_cube_array = Tile.objects.filter(id__in=allsearchtags).values_list('cube_id', flat=True)
            all_cube_id = Cube.objects.filter(id__in=pre_cube_array).values_list('id', flat=True).distinct('id')
            allsearchcubes = Cube.objects.filter(id__in=all_cube_id).order_by('-updated_at')
            number_of_cubes = Cube.objects.filter(id__in=all_cube_id).count()
        else:
            allsearchcubes = []
            number_of_cubes = 0
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


class TileFavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = TileFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tile = serializer.validated_data['tile']
        is_favorited = TileFavorites.objects.filter(user=request.user, tile=tile).exists()

        if is_favorited:
            return Response(
                {
                    "result": True,
                    "data": {
                        "tile": {
                            "tile_id": tile.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            favorite = TileFavorites(user=request.user, tile=tile)
            favorite.save()
            if request.user != tile.cube.user:
                history = History(From=request.user,
                                  To=tile.cube.user,
                                  tile=tile,
                                  cube=tile.cube,
                                  type=5)
                history.save()
                tile_favorite_notification.delay(request.user, tile.cube.user)
            return Response(
                {
                    "result": True,
                    "data": {
                        "tile": {
                            "tile_id": tile.id,
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )


class TileUnfavoriteView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    serializer_class = TileFavoriteSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tile = serializer.validated_data['tile']
        is_favorited = TileFavorites.objects.filter(user=request.user, tile=tile).exists()

        if is_favorited:
            TileFavorites.objects.filter(user=request.user, tile=tile).delete()
            return Response({"result": True}, status=status.HTTP_201_CREATED)
        else:
            return Response({"result": True}, status=status.HTTP_201_CREATED)


class AllTileView(GenericAPIView):

    def get(self, request):
        tiles = Tile.objects.filter(photo_url__icontains='https://res.cloudinary.com')
        Tiles = []
        for tile in tiles:
            cube = tile.cube
            tags = HashTags.objects.filter(tile=tile)

            Tags = []
            if tags:
                for tag in tags:
                    Tags.append(tag.tag)
            Tiles.append({
                    **serialize_tile(tile),
                    "cube_id": cube.id,
                    "cube_type": cube.type,
                    "tags": Tags
                })

        return Response(
            {
                "result": True,
                "data": {
                    "tiles": Tiles
                }
            },
            status=status.HTTP_201_CREATED
        )
