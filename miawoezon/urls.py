import os
from django.contrib import admin
from django.urls import path, include
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



def trigger_error(request):
    division_by_zero = 1 / 0



urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", include("main.urls")),
    path("rooms/", include("rooms.urls", namespace="rooms")),
    path("authentication/", include("authentication.urls", namespace="authentication")),
    path("reservations/", include("reservations.urls", namespace="reservations")),
    path("lists/", include("lists.urls", namespace="lists")),
    path("announcements/", include("announcement.urls", namespace="announcement")),
    path("blog/", include("blog.urls")),
    path("conversations/", include("conversations.urls")),
    path(os.environ.get("ADMIN_URL", "admin/"), admin.site.urls),
    path("sentry-debug/", trigger_error),
    path('accounts/', include('allauth.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
