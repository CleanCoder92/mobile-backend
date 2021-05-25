from django.urls import path
from .views import UserDetailView, UserProfileEditView, FollowView, UnFollowView, GetFollowersView, GetFollowingView,\
    SearchDetailView, NotificationCountView, NotificationListView, NotificationView, UserReportView, FCMToken, \
    RemoveMeView

app_name = 'users'

urlpatterns = [
    path('<int:pk>/', UserDetailView.as_view()),
    path('fcm/', FCMToken.as_view()),
    path('edit/', UserProfileEditView.as_view()),
    path('following/', FollowView.as_view()),
    path('unfollowing/', UnFollowView.as_view()),
    path('followers/<int:pk>/', GetFollowersView.as_view()),
    path('following/<int:pk>/', GetFollowingView.as_view()),
    path('search/', SearchDetailView.as_view()),
    path('notification_count/', NotificationCountView.as_view()),
    path('notification/', NotificationListView.as_view()),
    path('notification/<int:pk>/', NotificationView.as_view()),
    path('report/<int:pk>/', UserReportView.as_view()),
    path('remove-me/', RemoveMeView.as_view())
]
