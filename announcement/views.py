from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from announcement.forms import CommentForm, CreateHouseForm, CreatePhotoForm, PhotoUploadForm
from django.contrib.auth.mixins import LoginRequiredMixin
from announcement.models import House, Comment, Photo
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.forms import modelformset_factory

from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import House, Photo
from .forms import CreateHouseForm, PhotoFormSet


user_login_url = "authentication:login"
PhotoFormSet = modelformset_factory(Photo, form=PhotoUploadForm, extra=1, can_delete=True)

# Create your views here.
def announce_detail(request, pk):
    house = House.objects.get(pk=pk)
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                house=house,
            )
            comment.save()
            return HttpResponseRedirect(request.path_info)

    comments = Comment.objects.filter(house=house)
    context = {
        "house": house,
        "comments": comments,
        "form": CommentForm(),
    }
    return render(request, "house_detail.html", context)


# -------------------------- ROOMS -------------------#

# CREATE
class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    form_class = CreateHouseForm
    template_name = "house_create.html"
    success_url = reverse_lazy("announcement:host-list")
    login_url = reverse_lazy("user_login_url")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            data['formset'] = PhotoFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photos = context['formset']
        form.instance.host = self.request.user.client
        if form.is_valid() and photos.is_valid():
            self.object = form.save()
            photos.instance = self.object
            photos.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    

# LIST
class HouseHostListView(ListView):
    model = House
    context_object_name = "houses"
    template_name = "house_list.html"
    login_url = reverse_lazy(user_login_url)

    def get_queryset(self):
        return House.objects.filter(host=self.request.user.client).order_by(
            "-date"
        )

    def get_context_data(self, **kwargs):
        context = super(HouseHostListView, self).get_context_data(**kwargs)
        
        # Add the total_houses count to the context
        context["total_houses"] = House.objects.filter(host=self.request.user.client).count()
        return context
    

class AnnounceListView(ListView):
    model = House
    paginate_by = 30
    context_object_name = "announces"
    template_name = "announce_listing.html"

    def get_queryset(self):
        return House.objects.all().order_by("-date")

    def get_context_data(self, **kwargs):
        context = super(AnnounceListView, self).get_context_data(**kwargs)
        return context
    

# DETAIL
class HouseDetailView(DetailView):
    model = House
    context_object_name = "house"
    template_name = "house_detail.html"



# UPDATE
class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = CreateHouseForm
    template_name = "house_edit.html"
    success_url = reverse_lazy("announcement:host-list")
    login_url = reverse_lazy(user_login_url)

    def get_context_data(self, **kwargs):
        context = super(HouseUpdateView, self).get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context
    

# DELETE
class HouseDeleteView(LoginRequiredMixin, DeleteView):
    model = House
    success_url = reverse_lazy("announcement:host-list")
    template_name = "house_confirm_delete.html"

# -------------------------- HOUSE PHTOS -------------------#


class HousePhotosView(LoginRequiredMixin, DetailView):

    model = House
    template_name = "house_photo_list.html"

    def get_object(self, queryset=None):
        house = super().get_object(queryset=queryset)
        if house.host.pk != self.request.user.client.pk:
            raise Http404()
        return house


def delete_photo(request, house_pk, photo_pk):
    user = request.user.client
    try:
        house = House.objects.get(pk=house_pk)
        if house.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo deleted")
        return redirect(reverse("announcement:photo-list", kwargs={"pk": house_pk}))
    except House.DoesNotExist:
        return redirect(reverse("main:home"))


class EditPhotoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = Photo
    template_name = "house_photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated"
    fields = ("caption",)

    def get_success_url(self):
        house_pk = self.kwargs.get("house_pk")
        return reverse("announcement:photo-list", kwargs={"pk": house_pk})


class AddPhotoView(LoginRequiredMixin, FormView):

    template_name = "house_photo_create.html"
    fields = ("caption", "file")
    form_class = CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("announcement:photo-list", kwargs={"pk": pk}))
