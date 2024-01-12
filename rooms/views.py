from django.http import Http404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    CreateView,
    DetailView,
    UpdateView,
    ListView,
    FormView,
)
from authentication.models import Client
from rooms.forms import CreatePhotoForm, CreateRoomForm
from rooms.models import Room, Photo
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import render, redirect, reverse






user_login_url = "authentication:login"


# -------------------------- ROOMS -------------------#

# CREATE
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = CreateRoomForm
    template_name = "room_create.html"
    success_url = reverse_lazy("rooms:list")
    login_url = reverse_lazy(user_login_url)

    def form_valid(self, form):
        form.instance.host = self.request.user.client
        print("success")
        return super(RoomCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RoomCreateView, self).get_context_data(**kwargs)
        return context
    

# LIST
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    context_object_name = "rooms"
    template_name = "room_list.html"
    login_url = reverse_lazy(user_login_url)

    def get_queryset(self):
        return Room.objects.filter(host=self.request.user.client).order_by(
            "-created"
        )

    def get_context_data(self, **kwargs):
        context = super(RoomListView, self).get_context_data(**kwargs)
        return context


# DETAIL
class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    context_object_name = "room"
    template_name = "room_detail.html"



# UPDATE
class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = CreateRoomForm
    template_name = "room_edit.html"
    success_url = reverse_lazy("rooms:list")
    login_url = reverse_lazy(user_login_url)

    def get_context_data(self, **kwargs):
        context = super(RoomUpdateView, self).get_context_data(**kwargs)
        return context
    

# -------------------------- ROOMS PHTOS -------------------#


class RoomPhotosView(LoginRequiredMixin, DetailView):

    model = Room
    template_name = "room_photo_list.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.client.pk:
            raise Http404()
        return room


def delete_photo(request, room_pk, photo_pk):
    user = request.user.client
    try:
        room = Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo deleted")
        return redirect(reverse("rooms:photo-list", kwargs={"pk": room_pk}))
    except Room.DoesNotExist:
        return redirect(reverse("main:home"))


class EditPhotoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = Photo
    template_name = "room_photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated"
    fields = ("caption",)

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photo-list", kwargs={"pk": room_pk})


class AddPhotoView(LoginRequiredMixin, FormView):

    template_name = "room_photo_create.html"
    fields = ("caption", "file")
    form_class = CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photo-list", kwargs={"pk": pk}))





