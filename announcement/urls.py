from django.urls import path
from . import views

app_name = "announcement"

urlpatterns = [
    path("detail/<int:pk>/", views.announce_detail, name="detail"),
    path("list/", views.AnnounceListView.as_view(), name="list"),

    path("create/", views.HouseCreateView.as_view(), name="create"),
    path("host-list/", views.HouseHostListView.as_view(), name="host-list"),
    path("<int:pk>", views.HouseDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.HouseUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete", views.HouseDeleteView.as_view(), name="delete_house"),

    path("<int:pk>/photo-list", views.HousePhotosView.as_view(), name="photo-list"),
    path("<int:pk>/photos/add/", views.AddPhotoView.as_view(), name="add-photo"),
    path("<int:room_pk>/photos/<int:photo_pk>/delete/", views.delete_photo, name="delete-photo"),
    path("<int:room_pk>/photos/<int:photo_pk>/edit/", views.EditPhotoView.as_view(), name="edit-photo")
   
]
