from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static



from . import views

urlpatterns = [
    path("", views.home , name="home"),
    path("coming-soon", views.coming_soon , name="coming-soon"),
   
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
