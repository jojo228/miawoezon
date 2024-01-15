from django.urls import path
from . import views

app_name = "announcement"

urlpatterns = [
    path("detail/<int:pk>/", views.announce_detail, name="detail"),
    # path("list/", views.HomeView.as_view(), name="list"),
   
]
