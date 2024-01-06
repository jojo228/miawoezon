# blog/urls.py

from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_detail, name="blog-detail"),
]