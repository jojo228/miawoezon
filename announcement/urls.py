from django.urls import path
from . import views

app_name = "announcement"

urlpatterns = [
    path("login/", views.HomeView.as_view(), name="home"),
   
]
