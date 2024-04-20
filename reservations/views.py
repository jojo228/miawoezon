from datetime import datetime, timezone
import json
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect
from reservations.utils import generate_transaction_id
from rooms.models import Room
# from reviews import forms as review_forms
from . import models
from . import models as reservation_models
from django.urls import reverse, reverse_lazy
from .models import BookedDay, PaymentInformation, Reservation, TransactionCounter
from cinetpay_sdk.s_d_k import Cinetpay
from reservations.models import Reservation  # Assuming you have a Commande class in commande.py
import os, requests
from .models import TransactionCounter


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
            

            # Créez une instance Reservation sans la sauvegarder pour le moment
            reservation = Reservation(
                guest=request.user.client,
                room=room_instance,
                check_in=start_date,
                check_out=end_date,
            )

            # # Obtenez le prochain numéro de compteur pour l'identifiant de transaction
            # transaction_id_counter = TransactionCounter.get_next_counter()
            
            # # Utilisez transaction_id_counter pour générer le transaction_id
            # transaction_id = generate_transaction_id(request.user, transaction_id_counter)

            # # Créez une instance PaymentInformation et liez-la à la réservation
            # payment_info = PaymentInformation.objects.create(
            #     transaction_id=transaction_id,
            #     amount=reservation.total_amount(),
            #     currency='XOF',  # Remplacez par la devise réelle
            #     # Ajoutez d'autres champs requis pour PaymentInformation
            # )
            # reservation.payment = payment_info

            # Enregistrez la réservation et le paiement
            reservation.save()



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


# def initiate_payment(request):
#     if request.method == 'POST':
#         try:
#             # Récupération des données du formulaire
#             data = json.loads(request.body)

#             # Récupération des données requises pour initier le paiement
#             apikey = "19583603556596c6116b91e6.90506747"
#             site_id = "5867973"
#             transaction_id = data['transaction_id']
#             amount = data['amount']
#             currency = data['currency']
#             customer_name = data['customer_name']
#             customer_surname = data['customer_surname']
#             description = data['description']
#             notify_url = data['notify_url']
#             return_url = data['return_url']
#             channels = data.get('channels', 'ALL')
#             alternative_currency = data.get('alternative_currency', '')
#             customer_email = data.get('customer_email', '')
#             customer_phone_number = data.get('customer_phone_number', '')
#             customer_address = data.get('customer_address', '')
#             customer_city = data.get('customer_city', '')
#             customer_country = data.get('customer_country', '')
#             customer_state = data.get('customer_state', '')
#             customer_zip_code = data.get('customer_zip_code', '')

#             # Enregistrement des informations de paiement dans la base de données
#             payment_info = PaymentInformation.objects.create(
#                 transaction_id=transaction_id,
#                 amount=amount,
#                 currency=currency,
#                 customer_name=customer_name,
#                 customer_surname=customer_surname,
#                 description=description,
#                 notify_url=notify_url,
#                 return_url=return_url
#                 # Ajoutez d'autres champs si nécessaire
#             )

#             # Données pour générer le lien de paiement
#             payment_data = {
#                 "apikey": apikey,
#                 "site_id": site_id,
#                 "transaction_id": transaction_id,
#                 "amount": amount,
#                 "currency": currency,
#                 "customer_name": customer_name,
#                 "customer_surname": customer_surname,
#                 "description": description,
#                 "notify_url": notify_url,
#                 "return_url": return_url,
#                 "channels": channels,
#                 "alternative_currency": alternative_currency,
#                 "customer_email": customer_email,
#                 "customer_phone_number": customer_phone_number,
#                 "customer_address": customer_address,
#                 "customer_city": customer_city,
#                 "customer_country": customer_country,
#                 "customer_state": customer_state,
#                 "customer_zip_code": customer_zip_code
#             }

#             # Réponse avec le lien de paiement généré
#             return JsonResponse({"payment_url": generate_payment_link(payment_data)})

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)

#     else:
#         return JsonResponse({"error": "Method not allowed"}, status=405)

# def generate_payment_link(data):
#     # Votre logique pour générer le lien de paiement avec CinetPay
#     # Utilisez les données fournies pour construire le lien de paiement
#     # et retournez le lien généré
#     return "URL_DU_PAIEMENT_GÉNÉRÉ"


# def checkout(request, payment_id):
#     payment_info = PaymentInformation.objects.get(pk=payment_id)
#     # Initialize Paygate client
#     apikey = os.getenv("CINETPAY_APIKEY") 
#     site_id = os.getenv("CINETPAY_SITEID")
#     client = Cinetpay(apikey, site_id)
#     # Initialize payment with Paygate
#     response = client.initiate_payment(payment_info)
#     # Process response and redirect user to Paygate checkout page
#     return redirect(response['redirect_url'])



# def initiate_payment(request, reservation_id):
#         # Retrieve the reservation
#         reservation = Reservation.objects.get(pk=reservation_id)

#         # Your Cinetpay API credentials
#         apikey = os.getenv("CINETPAY_APIKEY") 
#         site_id = os.getenv("CINETPAY_SITEID")

#         # Initialize Cinetpay
#         client = Cinetpay(apikey, site_id)
        

#         # Assuming you have retrieved the necessary data for the payment
#         payment_data = {
#             'amount': int(reservation.room.price),  # Replace with the actual amount
#             'currency': 'XOF',
#             'channels': 'ALL',
#             'transaction_id': TransactionCounter.get_next_counter(),
#             'description': 'Payment for reservation',
#             # ... (other required data)
#         }

#         # Make the payment initialization request
#         payment_response = client.PaymentInitialization(payment_data)
#         print(payment_response)

#         # Check the payment_response and handle accordingly (e.g., redirect to payment gateway)

#         # Save the payment information in your database
#         if payment_response.get('code') == '00':
#             payment = PaymentInformation.objects.create(
#                 reservation=reservation,  # Associate payment with the reservation
#                 amount=payment_data['amount'],
#                 currency=payment_data['currency'],
#                 transaction_id=payment_data['transaction_id'],
#                 description=payment_data['description'],
#                 status='pending'  # You may update the status based on the payment response
#             )
#             payment.save()

#             # Redirect to a payment confirmation or gateway URL
#             return redirect(payment_response.get('payment_url'))
#         else:
#             return HttpResponse("Echec !!!")
#             # Handle the case when the payment initialization fails
#             # ...


def handle_payment_notification(request, cpm_trans_id):
    if request.method == 'POST':
        # Check if the request contains the required headers
        if 'x-token' not in request.headers:
            return JsonResponse({'error': 'Missing HMAC token'}, status=400)
        
        # Retrieve the HMAC token from the header
        hmac_token = request.headers['x-token']
        
        # Perform HMAC token verification (implementation not provided here)

        # Retrieve form values
        cpm_site_id = request.POST.get('cpm_site_id')
        cpm_trans_date = request.POST.get('cpm_trans_date')
        cpm_amount = request.POST.get('cpm_amount')
        cpm_currency = request.POST.get('cpm_currency')
        payment_method = request.POST.get('payment_method')
        cel_phone_num = request.POST.get('cel_phone_num')
        cpm_phone_prefixe = request.POST.get('cpm_phone_prefixe')
        cpm_language = request.POST.get('cpm_language')
        cpm_version = request.POST.get('cpm_version')
        cpm_payment_config = request.POST.get('cpm_payment_config')
        cpm_page_action = request.POST.get('cpm_page_action')
        cpm_custom = request.POST.get('cpm_custom')
        cpm_designation = request.POST.get('cpm_designation')
        cpm_error_message = request.POST.get('cpm_error_message')
        signature = request.POST.get('signature')

        # Check if cpm_site_id and cpm_trans_id are provided
        if cpm_site_id is None or cpm_trans_id is None:
            return JsonResponse({'error': 'Missing cpm_site_id or cpm_trans_id'}, status=400)

        # Check if payment status is already successful in your database
        try:
            payment_info = PaymentInformation.objects.get(transaction_id=cpm_trans_id)
            if payment_info.status == 'COMPLETED':
                return JsonResponse({'message': 'Payment already completed'}, status=200)
        except PaymentInformation.DoesNotExist:
            pass  # Payment information does not exist, proceed to verification

        # Call transaction verification API to obtain transaction status from CinetPay
        apikey = os.getenv("CINETPAY_APIKEY") 
        site_id = os.getenv("CINETPAY_SITEID")
        data = {
            "apikey": apikey,
            "site_id": site_id,
            "transaction_id": cpm_trans_id,
        }
        verification_response = requests.post(
            url="https://api-checkout.cinetpay.com/v2/payment/check",
            data=data
        )
        
        print(verification_response)
        # Handle verification response (implementation not provided here)

        # Update payment status in your database based on verification response
        # For example, if verification_response indicates successful payment:
        # payment_info.status = 'COMPLETED'
        # payment_info.save()

        return JsonResponse({'message': 'Payment notification processed'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    


def handle_payment_return(request):
    if 'cpm_trans_id' in request.POST or 'token' in request.POST:
        try:
            id_transaction = request.POST.get('transaction_id') or request.POST.get('token')

            # Initialisation de CinetPay et vérification du statut de paiement
            apikey = os.getenv("CINETPAY_APIKEY") 
            site_id = os.getenv("CINETPAY_SITEID")
            client = Cinetpay(apikey, site_id)
            client.getPayStatus(id_transaction, site_id)    

            # Récupération du message et du code de statut de CinetPay
            message = client.chk_message
            code = client.chk_code

            # Redirection vers une page en fonction de l'état de la transaction
            if code == '00':
                return redirect("reservations:invoice")
            else:
                return redirect("reservations:invoice")
        except Exception as e:
            return HttpResponse("Erreur : " + str(e))
    else:
        return HttpResponse('transaction_id non transmis')