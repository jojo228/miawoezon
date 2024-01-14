import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
# from reviews import forms as review_forms
from . import models


class CreateError(Exception):
    pass


from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from . import models as reservation_models
from rooms import models as room_models


def create(request, room, year, month, day):
    try:
        # Extract start and end dates from the form data
        start_date = datetime(year, month, day)
        end_date = datetime.strptime(request.POST.get('bookdates'), '%Y-%m-%d')

        room_instance = room_models.Room.objects.get(pk=room)

        # Check if any booked day exists within the selected range
        existing_booked_day = reservation_models.BookedDay.objects.filter(
            day__range=(start_date, end_date),
            reservation__room=room_instance
        ).exists()

        if existing_booked_day:
            raise CreateError()

        reservation = reservation_models.Reservation.objects.create(
            guest=request.user.client,
            room=room_instance,
            check_in=start_date,
            check_out=end_date,
        )

        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))

    except room_models.Room.DoesNotExist:
        messages.error(request, "Can't Reserve That Room'")
        return redirect(reverse("home"))
    except reservation_models.BookedDay.DoesNotExist:
        messages.error(request, "Selected date range is not available")
        return redirect(reverse("home"))
    except CreateError:
        messages.error(request, "The room is already booked for the selected dates")
        return redirect(reverse("home"))



class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            raise Http404()
        # form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "booking-detail.html",
            # {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()
    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation Updated")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))
