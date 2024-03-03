from datetime import datetime
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect
from rooms.models import Room
# from reviews import forms as review_forms
from . import models
from . import models as reservation_models
from django.urls import reverse, reverse_lazy
from .models import BookedDay, Payment, Reservation
from cinetpay_sdk.s_d_k import Cinetpay
from reservations.models import Reservation  # Assuming you have a Commande class in commande.py

class CreateError(Exception):
    pass


def bookings(request):
    client = request.user.client
    total_rooms = Room.objects.filter(host=client).count()
    total_reservations = Reservation.objects.filter(room__host=client).count()
    bookings =  Reservation.objects.filter(guest=client).order_by('-created')
    
    return render(request, "bookings.html", locals())


def my_bookings(request):
    client = request.user.client
    total_rooms = Room.objects.filter(host=client).count()
    total_reservations = Reservation.objects.filter(room__host=client).count()
    bookings =  Reservation.objects.filter(guest=client).order_by('-created')
    
    return render(request, "mybookings.html", locals())


class CreateReservationView(LoginRequiredMixin, View):
    def post(self, request, room):
        try:
            # Extract combined start and end dates from the form data
            date_range_str = request.POST.get('bookdates')
            
            # Split the date range into start and end date strings
            start_date_str, end_date_str = map(str.strip, date_range_str.split('-'))

            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date = datetime.strptime(end_date_str, '%m/%d/%Y')

            room_instance = Room.objects.get(pk=room)
            
            # Check if any booked day exists within the selected range
            existing_booked_day = BookedDay.objects.filter(
                day__range=(start_date, end_date),
                reservation__room=room_instance
            ).exists()

            if existing_booked_day:
                raise CreateError()

            reservation = Reservation.objects.create(
                guest=request.user.client,
                room=room_instance,
                check_in=start_date,
                check_out=end_date,
            )

            return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))

        except Room.DoesNotExist:
            messages.error(request, "Can't Reserve That Room")
            return redirect(reverse("rooms:detail", kwargs={"pk": room}))
        except BookedDay.DoesNotExist:
            messages.error(request, "Selected date range is not available")
            return redirect(reverse("rooms:detail", kwargs={"pk": room}))
        except CreateError:
            messages.error(request, "The room is already booked for the selected dates")
            return redirect(reverse("rooms:detail", kwargs={"pk": room}))

# Custom exception class
class CreateError(Exception):
    pass



class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user.client
            and reservation.room.host != self.request.user.client
        ):
            raise Http404()
        # form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "booking-detail.html", locals()
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


def invoice(request):

    return render(request, "invoice.html")



def initiate_payment(request, reservation_id):
    try:
        # Retrieve the reservation
        reservation = Reservation.objects.get(pk=reservation_id)

        # Your Cinetpay API credentials
        apikey = "19583603556596c6116b91e6.90506747"
        site_id = "5867973"

        # Initialize Cinetpay
        client = Cinetpay(apikey, site_id)

        # Assuming you have retrieved the necessary data for the payment
        payment_data = {
            'amount': int(reservation.room.price),  # Replace with the actual amount
            'currency': 'XOF',
            'transaction_id': 'your_unique_transaction_id',
            'description': 'Payment for reservation',
            # ... (other required data)
        }

        # Make the payment initialization request
        payment_response = client.PaymentInitialization(payment_data)
        print(payment_response)

        # Check the payment_response and handle accordingly (e.g., redirect to payment gateway)

        # # Save the payment information in your database
        # if payment_response.get('code') == '00':
        #     payment = Payment.objects.create(
        #         reservation=reservation,  # Associate payment with the reservation
        #         amount=payment_data['amount'],
        #         currency=payment_data['currency'],
        #         transaction_id=payment_data['transaction_id'],
        #         description=payment_data['description'],
        #         status='pending'  # You may update the status based on the payment response
        #     )

        #     # Redirect to a payment confirmation or gateway URL
        #     return redirect(payment_response.get('payment_url'))
        # else:
        #     pass
        #     # Handle the case when the payment initialization fails
        #     # ...

    except Reservation.DoesNotExist:
        messages.error(request, "Reservation not found")
        return redirect(reverse("main:home"))
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect(reverse("main:home"))


def check_transaction_by_id(request, transaction_id):
    # Your Cinetpay API credentials
    apikey = "19583603556596c6116b91e6.90506747"
    site_id = "5867973"

    # Initialize Cinetpay
    client = Cinetpay(apikey, site_id)

    # Check the transaction status by transaction ID
    response = client.TransactionVerfication_trx(transaction_id)

    # Process the response and return a JSON response
    return JsonResponse(response)



def check_transaction_by_token(request, token):
    # Your Cinetpay API credentials
    apikey = "19583603556596c6116b91e6.90506747"
    site_id = "5867973"

    # Initialize Cinetpay
    client = Cinetpay(apikey, site_id)

    # Check the transaction status by token
    response = client.TransactionVerfication_token(token)

    # Process the response and return a JSON response
    return JsonResponse(response)


def notification(request):

    if 'cpm_trans_id' in request.POST:
        try:
            # Création d'un fichier log pour s'assurer que les éléments sont bien exécutés
            log = "User: " + request.META.get('REMOTE_ADDR') + ' - ' + datetime.now().strftime("%B %d, %Y, %I:%M %p") + '\n'
            log += "TransId: " + request.POST['cpm_trans_id'] + '\n'
            log += "SiteId: " + request.POST['cpm_site_id'] + '\n'
            log += "-------------------------\n"
            
            # Save string to log
            with open('log_' + datetime.now().strftime("%d.%m.%Y") + '.log', 'a') as logfile:
                logfile.write(log)

            # La classe Commande correspond à votre colonne qui gère les transactions dans votre base de données
            commande = Reservation()
            # Initialisation de CinetPay et Identification du paiement
            id_transaction = request.POST['cpm_trans_id']
            apikey = "19583603556596c6116b91e6.90506747"
            site_id = "5867973"

            cinetpay = Cinetpay(site_id, apikey)
            # On recupère le statut de la transaction dans la base de données
            # $commande->set_transactionId($id_transaction);
            # $commande->getCommandeByTransId();

            # On vérifie que la commande n'a pas encore été traitée
            VerifyStatusCmd = "1"  # valeur du statut à récupérer dans votre base de données
            if VerifyStatusCmd == '00':
                # La commande a été déjà traitée
                # Arrêt du script
                return

            # Dans le cas contraire, on vérifie l'état de la transaction en cas de tentative de paiement sur CinetPay
            cinetpay.getPayStatus(id_transaction, site_id)

            amount = cinetpay.chk_amount
            currency = cinetpay.chk_currency
            message = cinetpay.chk_message
            code = cinetpay.chk_code
            metadata = cinetpay.chk_metadata

            # Something to write to txt log
            log = "User: " + request.META.get('REMOTE_ADDR') + ' - ' + datetime.now().strftime("%B %d, %Y, %I:%M %p") + '\n'
            log += "Code:" + code + '\n'
            log += "Message: " + message + '\n'
            log += "Amount: " + amount + '\n'
            log += "currency: " + currency + '\n'
            log += "-------------------------\n"
            
            # Save string to log
            with open('log_' + datetime.now().strftime("%d.%m.%Y") + '.log', 'a') as logfile:
                logfile.write(log)

            # On vérifie que le montant payé chez CinetPay correspond à notre montant en base de données pour cette transaction
            if code == '00':
                # correct, on délivre le service
                print('Félicitation, votre paiement a été effectué avec succès')
                return

            else:
                # transaction n'est pas valide
                print('Échec, votre paiement a échoué pour cause : ' + message)
                return
            # mise à jour des transactions dans la base de données
            # commande.update();

        except Exception as e:
            print("Erreur :" + str(e))

    else:
        # direct access on IPN
        print("cpm_trans_id non fourni")
