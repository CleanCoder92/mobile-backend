from django.urls import path
from cubes import views

app_name = 'cubes'

urlpatterns = [
    path('', views.CubeListView.as_view()),
    path('<int:pk>/', views.CubeDetailView.as_view()),
    path('discover/', views.DiscoverCubesView.as_view()),
    path('following/', views.FollowingCubesView.as_view()),
    path('all/', views.AllCubesView.as_view()),
    path('favorite/', views.CubeFavoriteView.as_view()),
    path('unfavorite/', views.CubeUnfavoriteView.as_view()),
    path('create/', views.CubeCreateView.as_view()),
    path('update/', views.CubeUpdateView.as_view()),
    path('comment/<int:pk>/', views.CubeCommentView.as_view()),
    path('comment/create/', views.CommentCreateView.as_view()),
    path('comment/favorite/', views.CommentFavoriteView.as_view()),
    path('comment/unfavorite/', views.CommentUnfavoriteView.as_view()),
    path('comment2/create/', views.SubscriptionCreateView.as_view()),
    path('search/', views.SearchDetailView.as_view()),
    path('report/<int:pk>/', views.CubeReportlView.as_view()),
]
