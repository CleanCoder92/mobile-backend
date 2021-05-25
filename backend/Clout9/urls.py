from django.urls import re_path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    re_path(r"^api/v1/", include('api.urls')),
    re_path(r"^share/", include('share.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

