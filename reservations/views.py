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
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.utils.decorators import method_decorator
from django.conf import settings

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


@method_decorator(csrf_exempt, name='dispatch')
class PaymentInitializationView(View):

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the reservation using the pk from the URL
            pk = kwargs.get("pk")
            if not pk:
                return JsonResponse({'error': 'Reservation ID is missing.'}, status=400)

            reservation = Reservation.objects.get(pk=pk)

            # Return reservation details for confirmation
            reservation_data = {
                'reservation_id': reservation.id,
                'room': str(reservation.room),
                'total_amount': reservation.total_amount(),
                'status': reservation.status,
                'check_in': reservation.check_in,
                'check_out': reservation.check_out
            }
            return JsonResponse(reservation_data, status=200)

        except Reservation.DoesNotExist:
            return JsonResponse({'error': 'Reservation not found'}, status=404)

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve data and process payment (POST request to initiate payment)
            pk = kwargs.get("pk")
            if not pk:
                return JsonResponse({'error': 'Reservation ID is missing.'}, status=400)

            reservation = Reservation.objects.get(pk=pk)

            # Total amount for payment
            total_amount = reservation.total_amount()
            if total_amount <= 0:
                return JsonResponse({'error': 'Le montant total doit être supérieur à zéro.'}, status=400)

            # Process payment initialization with CinetPay (same as before)
            transaction_id = str(uuid.uuid4())
            cinetpay_data = {
                'apikey': settings.CINETPAY_API_KEY,
                'site_id': settings.CINETPAY_SITE_ID,
                'transaction_id': transaction_id,
                'amount': str(total_amount),
                'currency': 'XOF',
                'channels': 'ALL',
                'description': 'Paiement de commande',
                'return_url': request.build_absolute_uri('/payment/return/'),
                'notify_url': request.build_absolute_uri('/payment/notify/'),
                'customer_name': request.user.username if request.user.is_authenticated else 'Anonymous',
                'customer_email': request.user.email if request.user.is_authenticated else 'anonymous@example.com',
                'customer_phone_number': '00000000',  # Update as needed
                'customer_address': request.POST.get('address'),
                'customer_city': request.POST.get('city'),
                'customer_country': request.POST.get('country'),
            }

            # Send payment request to CinetPay
            response = requests.post('https://api-checkout.cinetpay.com/v2/payment', json=cinetpay_data)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('code') == '201':
                payment_url = response_data['data']['payment_url']
                return JsonResponse({'payment_url': payment_url})

            else:
                error_message = response_data.get('description', 'Une erreur est survenue lors de l\'initialisation du paiement.')
                return JsonResponse({'error': error_message}, status=400)

        except Reservation.DoesNotExist:
            return JsonResponse({'error': 'Reservation not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def payment_notify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extraire les données importantes de la notification
            transaction_id = data.get('cpm_trans_id')
            amount = data.get('cpm_amount')
            status = data.get('cpm_trans_status')

            # Vérifiez que les données nécessaires sont présentes
            if not transaction_id or not amount or not status:
                return JsonResponse({'error': 'Missing transaction data.'}, status=400)

            # Récupérer le paiement correspondant
            try:
                payment = PaymentInformation.objects.get(transaction_id=transaction_id)
            except PaymentInformation.DoesNotExist:
                return JsonResponse({'error': 'Transaction not found.'}, status=404)

            # Mise à jour du statut en fonction du statut de la transaction
            if status == '00':
                payment.status = 'COMPLETED'
                payment.order.ordered = True  # Marquer la commande comme complète
                payment.order.save()
            else:
                payment.status = 'FAILED'

            payment.save()

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



@method_decorator(csrf_exempt, name='dispatch')
class PaymentReturnView(View):
    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('transaction_id')
        
        if not transaction_id:
            return JsonResponse({"error": "Transaction ID not provided."}, status=400)

        # Configuration de l'API CinetPay
        api_url = "https://api.cinetpay.com/v1/?method=checkPayStatus"
        site_id = settings.CINETPAY_SITE_ID
        api_key = settings.CINETPAY_API_KEY

        # Préparation des données pour la requête à CinetPay
        data = {
            "apikey": api_key,
            "site_id": site_id,
            "transaction_id": transaction_id,
        }

        # Faire la requête à l'API de CinetPay
        response = requests.post(api_url, json=data)
        result = response.json()
        print(result)

        # Vérifiez que 'amount' et 'status' sont présents dans la réponse
        amount = result.get('amount')
        status = result.get('status')

        if amount is None or status is None:
            return JsonResponse({"error": "Invalid response from CinetPay. 'amount' or 'status' not found."}, status=400)

        payment, created = PaymentInformation.objects.create(
            transaction_id=transaction_id,
            defaults={
                'user': request.user,  # Relier le paiement à l'utilisateur
                'amount': amount,
                'status': status,
            }
        )

        # Vérifier le statut de la réponse
        if response.status_code == 200 and result.get('status') == '00':
            # Paiement réussi
            payment_status = "Success"

            # Mettre à jour ou créer les informations de paiement dans la base de données
            payment_info, created = PaymentInformation.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    'user': request.user,  # Relier le paiement à l'utilisateur
                    'amount': result['amount'],
                    'status': payment_status,  # Statut du paiement
                }
            )

            # Mise à jour du statut de la réservation liée à la commande (order dans PaymentInformation)
            reservation = payment_info.order
            reservation.status = Reservation.STATUS_CONFIRMED  # Statut de la réservation confirmé
            reservation.save()



        else:
            # Paiement échoué ou en attente
            payment_status = "Failed"
            PaymentInformation.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                'user': request.user,  # Relier le paiement à l'utilisateur
                'amount': result['amount'],
                'status': result['status'],
            }
        )

        # Rediriger vers une page de confirmation de paiement avec le statut
        return render(request, 'payment_return.html', {'payment_status': payment_status})
