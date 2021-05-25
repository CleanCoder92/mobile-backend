from django.urls import path

from .views import cube_view, url_view

app_name = 'share'

urlpatterns = [
    path('<int:pk>/', cube_view),
    path('url/<int:pk>/', url_view.as_view())
]
