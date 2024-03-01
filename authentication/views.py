from datetime import date
import os
from django.shortcuts import render, redirect
from authentication.forms import (
    ClientIdentityForm,
    ClientPersonalDataForm,
    ClientAddressForm,
)
from staff_account.models import User
from django.urls import reverse_lazy
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView

from django.views.generic import UpdateView, DetailView, RedirectView, TemplateView

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from authentication.models import Client

client_detail_url = "authentication:client_detail"


# Email activation importation
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage

# -------------------------- ACCOUNT -------------------#

# CREATE
class SignupWizardView(SessionWizardView):
    login_url = reverse_lazy("authentication:login")
    template_name = "signup.html"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos'))

    def send_activation_email(self, user):
        # We need the user object, so it's an additional parameter
        # account confirmation mail
        # to get the domain of the current site
        current_site = get_current_site(self.request)
        subject = "Un lien d'activation a été envoyée à votre addresse email"
        message = render_to_string(
            "activate_account.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
                "protocol": "https" if self.request.is_secure() else "http",
            },
        )
        user.email_user(subject, message, html_message=message)

    def done(self, form_list, **kwargs):

        # save the user created
        user = form_list[0].save(commit=False)
        # Automatic assign username to user based on last name, first_name, date joined , and make sure to create unique username
        username = ""
        # create username first string
        for name in user.first_name.split(" "):
            username += name[0].upper()
        username += user.last_name[0:2].upper()
        for name in user.first_name.split(" "):
            username += name[-1].upper()

        username += date.today().strftime("%y%m%d")
        next_username_number = "001"

        while User.objects.filter(username=username):
            username += next_username_number
            next_username_number = "{0:04d}".format(int(next_username_number) + 1)
        user.username = username

        # Add the user as inactive
        user.is_active = False

        # create a client linked to the user created and fill its identity data first
        client_personal_data = form_list[1].save(commit=False)
        client_personal_data.user = user

        # then use the identity form to complete the model
        client_personal_data.country = form_list[2].cleaned_data["country"]
        client_personal_data.city = form_list[2].cleaned_data["city"]
        client_personal_data.address = form_list[2].cleaned_data["address"]
        client_personal_data.pincode = form_list[2].cleaned_data["pincode"]

        # save forms ad last once everything is correct
        user.save()
        client_personal_data.save()
        self.send_activation_email(user)

        return redirect("authentication:check_email")


# The view to activate the user account after the email confirmation
class ActivateView(RedirectView):

    url = reverse_lazy("authentication:success")

    # Custom get method
    def get(self, request, uidb64, token):

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user, backend="gespro.authentication.backends.MyBackend")
            return super().get(request, uidb64, token)
        else:
            return render(request, "activate_account_invalid.html")


class CheckEmailView(TemplateView):
    template_name = "check_email.html"


class SuccessView(TemplateView):
    template_name = "success.html"


# READ
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = "client"
    template_name = "client_detail.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve the client object from the context
        client = context["client"]
        
        # Query the Room model to count the rooms associated with the client
        total_rooms = client.rooms.count()

        # Query the Room model to count the reservations associated with the client
        total_reservations = client.reservations.count()
        
        # Add the total_rooms count to the context
        context["total_rooms"] = total_rooms
        context["total_reservations"] = total_reservations
        
        return context


# UPDATE
class ClientIdentityInformationUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    context_object_name = "client"
    form_class = ClientIdentityForm
    template_name = "client_identity_information_update.html"

    def get_success_url(self):
        return reverse_lazy(
            client_detail_url,
            kwargs={"pk": Client.objects.get(user_id=self.kwargs["pk"]).id},
        )


class ClientPersonalInformationUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy("staff_account:login")
    model = Client
    context_object_name = "client"
    form_class = ClientPersonalDataForm
    template_name = "client_personal_information_update.html"

    def get_success_url(self):
        return reverse_lazy(client_detail_url, kwargs={"pk": self.kwargs["pk"]})


class ClientAddressUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy("staff_account:login")
    model = Client
    context_object_name = "client"
    form_class = ClientAddressForm
    template_name = "client_address_update.html"

    def get_success_url(self):
        return reverse_lazy(client_detail_url, kwargs={"pk": self.kwargs["pk"]})
