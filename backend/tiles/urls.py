from django.urls import path
from .views import TileCreateView, TileDetailView, TileCommentView, TileUpdateView, CommentCreateView, \
    SearchDetailView, SearchTagDetailView, SubscriptionCreateView, CommentFavoriteView, CommentUnfavoriteView, \
    TileFavoriteView, TileUnfavoriteView, AllTileView
app_name = 'tiles'

urlpatterns = [
    path('create/', TileCreateView.as_view()),
    path('update/', TileUpdateView.as_view()),
    path('<int:pk>/', TileDetailView.as_view()),
    path('comment/<int:pk>/', TileCommentView.as_view()),
    path('favorite/', TileFavoriteView.as_view()),
    path('unfavorite/', TileUnfavoriteView.as_view()),
    path('comment/create/', CommentCreateView.as_view()),
    path('comment/favorite/', CommentFavoriteView.as_view()),
    path('comment/unfavorite/', CommentUnfavoriteView.as_view()),
    path('comment2/create/', SubscriptionCreateView.as_view()),
    path('search/', SearchDetailView.as_view()),
    path('search/tag/', SearchTagDetailView.as_view()),
    path('all/', AllTileView.as_view()),
]
