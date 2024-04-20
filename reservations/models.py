import datetime
from django.conf import settings
from django.db import models
from django.shortcuts import redirect
from django.utils import timezone
from authentication.models import Client
from main import models as main_models
from django_countries.fields import CountryField # type: ignore



class BookedDay(main_models.TimeStampedModel):

    day = models.DateField()
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return str(self.day)


class Reservation(main_models.TimeStampedModel):

    """ Reservation Model Definition """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Cenceled"),
    )

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guest = models.ForeignKey(
        "authentication.Client", related_name="reservations", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = timezone.localtime().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        now = timezone.localtime().date()
        is_finished = now > self.check_out
        if is_finished:
            BookedDay.objects.filter(reservation=self).delete()
        return is_finished

    is_finished.boolean = True

    def total_days(self):
        start = self.check_in
        end = self.check_out
        difference = end - start
        return difference.days + 1
    
    def subtotal(self):
        days = self.total_days() 
        total = days * self.room.price
        return total
    

    def service_fees(self):
        total = self.subtotal()
        fee_percentage = 3 / 100
        fees = (total * fee_percentage)
        return fees
    
    def total_amount(self):
        total = self.subtotal() + self.service_fees()
        return total

    def save(self, *args, **kwargs):
        if self.pk is None:
            start = self.check_in
            end = self.check_out
            difference = end - start
            existing_booked_day = BookedDay.objects.filter(
                day__range=(start, end)
            ).exists()
            if not existing_booked_day:
                super().save(*args, **kwargs)
                for i in range(difference.days + 1):
                    day = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return super().save(*args, **kwargs)


class PaymentInformation(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    description = models.TextField()
    trans_date = models.DateTimeField(null=True)
    payment_method = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=50, null=True)
    phone_prefixe = models.CharField(max_length=50, null=True)
    language = models.CharField(max_length=50, null=True)
    phone_prefixe = models.CharField(max_length=50, null=True)
    notify_url = models.URLField()
    return_url = models.URLField()
    status = models.CharField(max_length=50, null=True)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    message = models.CharField(max_length=500, null=True)
    def __str__(self):
        return self.transaction_id
    

class BillingInformation(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2)  # Utilisez ISO 3166-1 alpha-2 codes
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return self.email


class TransactionCounter(models.Model):
    counter = models.IntegerField(default=1)

    @classmethod
    def get_next_counter(cls):
        # Obtenez l'instance de compteur unique ou créez-en une si elle n'existe pas encore
        counter_instance, created = cls.objects.get_or_create(pk=1)
        
        # Récupérez la valeur actuelle du compteur et incrémentez-la
        current_counter = counter_instance.counter
        next_counter = current_counter + 1
        
        # Mettez à jour le compteur dans la base de données
        counter_instance.counter = next_counter
        counter_instance.save()
        
        return current_counter
