from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from announcement.forms import CommentForm
from announcement.models import House, Comment


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