from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("create/", views.RoomCreateView.as_view(), name="create"),
    path("list/", views.RoomListView.as_view(), name="list"),
    path("<int:pk>", views.RoomDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.RoomUpdateView.as_view(), name="edit"),

    path("<int:pk>/photo-list", views.RoomPhotosView.as_view(), name="photo-list"),
    path("<int:pk>/photos/add/", views.AddPhotoView.as_view(), name="add-photo"),
    path("<int:room_pk>/photos/<int:photo_pk>/delete/", views.delete_photo, name="delete-photo"),
    path("<int:room_pk>/photos/<int:photo_pk>/edit/", views.EditPhotoView.as_view(), name="edit-photo")
    
    # path("search/", views.search, name="search"),
]
