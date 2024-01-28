from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from announcement.forms import CommentForm
from announcement.models import House, Comment
from django.urls import reverse_lazy



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
    return render(request, "detail.html", context)


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