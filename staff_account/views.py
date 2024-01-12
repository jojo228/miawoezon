from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from staff_account.forms import (
    StaffAddressForm,
    StaffIdentityForm,
    StaffPersonalDataForm,
)
from staff_account.forms import StaffForm
from staff_account.models import Staff
from authentication.forms import CustomUserCreationForm
from staff_account.models import User
from django.contrib.auth.models import Group
from formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
    DetailView,
    DeleteView,
    RedirectView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Email activation importation
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from authentication.token import account_activation_token
from django.core.mail import EmailMessage


staff_account_detail_url = "staff_account:staff_account_detail"
staff_detail_url = "staff_account:staff_detail"
staff_login_url = "staff_account:login"
staff_account_list_url = "staff_account:staff_account_list"


class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy(staff_login_url)

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


# -------------------------- ACCOUNT -------------------#

# DETAIL
class StaffDetailView(AdminStaffRequiredMixin, DetailView):
    model = Staff
    context_object_name = "staff"
    template_name = "staff_account/staff_detail.html"


# UPDATE
class StaffIdentityInformationUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    context_object_name = "staff"
    form_class = StaffIdentityForm
    template_name = "staff_account/staff_identity_information_update.html"

    def get_success_url(self):
        return reverse_lazy(
            staff_detail_url,
            kwargs={"pk": Staff.objects.get(user_id=self.kwargs["pk"]).id},
        )


class StaffPersonalInformationUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy(staff_login_url)
    model = Staff
    context_object_name = "staff"
    form_class = StaffPersonalDataForm
    template_name = "staff_account/staff_personal_information_update.html"

    def get_success_url(self):
        return reverse_lazy(staff_detail_url, kwargs={"pk": self.kwargs["pk"]})


class StaffAddressUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy(staff_login_url)
    model = Staff
    context_object_name = "staff"
    form_class = StaffAddressForm
    template_name = "staff_account/staff_address_update.html"

    def get_success_url(self):
        return reverse_lazy(staff_detail_url, kwargs={"pk": self.kwargs["pk"]})


# -------------------------- STAFF MANAGEMENT -------------------#

# CREATE
class SignupWizardView(SessionWizardView):
    login_url = reverse_lazy(staff_login_url)
    template_name = "staff_account/staff_account_create.html"

    def send_activation_email(self, user):
        # We need the user object, so it's an additional parameter
        # account confirmation mail
        # to get the domain of the current site
        current_site = get_current_site(self.request)
        subject = "Un lien d'activation a été envoyée à votre addresse email"
        message = render_to_string(
            "staff_account/activate_account.html",
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

        # create a staff linked to the user created and fill its identity data first
        staff_personal_data = form_list[1].save(commit=False)
        staff_personal_data.user = user

        # then use the identity form to complete the model
        staff_personal_data.country = form_list[2].cleaned_data["country"]
        staff_personal_data.city = form_list[2].cleaned_data["city"]
        staff_personal_data.address = form_list[2].cleaned_data["address"]
        staff_personal_data.pincode = form_list[2].cleaned_data["pincode"]

        # save forms ad last once everything is correct
        user.save()
        staff_personal_data.save()
        self.send_activation_email(user)

        return redirect("staff_account:check_email")


# The view to activate the user account after the email confirmation
class ActivateView(RedirectView):

    url = reverse_lazy("staff_account:success")

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
            return render(request, "staff_account/activate_account_invalid.html")


class CheckEmailView(TemplateView):
    template_name = "staff_account/check_email.html"


class SuccessView(TemplateView):
    template_name = "staff_account/success.html"


# LIST
class StaffListView(AdminStaffRequiredMixin, ListView):
    model = Staff
    context_object_name = "staffs"
    template_name = "staff_account/staff_account_list.html"

    def get_queryset(self):
        object_list = Staff.objects.filter(user__is_superuser=False)

        return object_list


class StaffAccountDetailView(AdminStaffRequiredMixin, DetailView):
    model = Staff
    context_object_name = "staff"
    template_name = "staff_account/staff_account_detail.html"


# UPDATE
class StaffAccountIdentityInformationUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    context_object_name = "staff"
    form_class = StaffIdentityForm
    template_name = "staff_account/staff_account_identity_information_update.html"

    def get_success_url(self):
        return reverse_lazy(
            staff_account_detail_url,
            kwargs={"pk": Staff.objects.get(user_id=self.kwargs["pk"]).id},
        )


class StaffAccountPersonalInformationUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy(staff_login_url)
    model = Staff
    context_object_name = "staff"
    form_class = StaffPersonalDataForm
    template_name = "staff_account/staff_account_personal_information_update.html"

    def get_success_url(self):
        return reverse_lazy(staff_account_detail_url, kwargs={"pk": self.kwargs["pk"]})


class StaffAccountAddressUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy(staff_login_url)
    model = Staff
    context_object_name = "staff"
    form_class = StaffAddressForm
    template_name = "staff_account/staff_account_address_update.html"

    def get_success_url(self):
        return reverse_lazy(staff_account_detail_url, kwargs={"pk": self.kwargs["pk"]})


# DELETE
class StaffAccountDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy(staff_account_list_url)
