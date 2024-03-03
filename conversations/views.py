from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from authentication import models as user_models
from reservations.models import Reservation
from rooms.models import Room
from . import models, forms


def dashboardmessages(request):
    total_rooms = Room.objects.filter(host=request.user.client).count()
    total_reservations = Reservation.objects.filter(room__host=request.user.client).count()
    return render(request, "conversations_list.html", locals())


def go_conversation(request, a_pk, b_pk):
    user_one = user_models.Client.objects.get(pk=a_pk)
    user_two = user_models.Client.objects.get(pk=b_pk)
    if user_one is not None and user_two is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=user_one) & Q(participants=user_two)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_one, user_two)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get(pk=pk)
        if not conversation:
            raise Http404()
        return render(
            self.request,
            "conversation_detail.html",
            {"conversation": conversation},
        )

    def post(self, *args, **kwargs):
        message = self.request.POST.get("message", None)
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get(pk=pk)
        if not conversation:
            raise Http404()
        if message is not None:
            models.Message.objects.create(
                message=message, user=self.request.user.client, conversation=conversation
            )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
