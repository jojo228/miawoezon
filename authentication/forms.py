from django import forms
from django.forms import ModelForm
from .models import Client
from staff_account.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm,
)
import unicodedata

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm


# ---------------------------------Utilities classes-----------------------------------------------#

# custom widget type for display date in html input date format
class DateInput(forms.DateInput):
    input_type = "date"


# ---------------------------------Signup and account Forms-----------------------------------------#


class CustomUserCreationForm(UserCreationForm):

    """
    A form that creates a user, with no privileges, from the given name, email and
    password.
    """

    error_messages = {
        "password_mismatch": _("Les deux mots de passe ne sont pas identiques"),
    }
    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Répéter le mot de passe précédent, pour verification."),
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )
        labels = {
            "first_name": "Prénom.s",
            "last_name": "Nom",
            "email": "Email",
        }


class ClientIdentityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientIdentityForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Prénom.s",
            "last_name": "Nom",
            "email": "Email",
        }


class ClientPersonalDataForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientPersonalDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "
        
        # Add class to the select widgets for "sex" and "matrimonial_status"
        self.fields['sex'].widget.attrs["class"] = "chosen-select no-search-select"
        self.fields['matrimonial_status'].widget.attrs["class"] = "chosen-select no-search-select"

    class Meta:
        model = Client
        fields = ("date_of_birth", "matrimonial_status", "contact", "profession", "sex",)
        labels = {
            "date_of_birth": "Date de naissance",
            "sex": "Sexe",
            "matrimonial_status": "Statut Matrimonial",
            "profession": "Profession",
        }
        widgets = {"date_of_birth": DateInput()}


class ClientAddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientAddressForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta:
        model = Client
        fields = ("country", "city", "address", "pincode")
        labels = {
            "country": "Pays",
            "city": "Ville",
            "address": "Adresse",
            "pincode": "PINCODE",
        }


# ---------------------------------Custom Password Reset Forms--------------------------------------------#


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "


class CustomSetPasswordForm(SetPasswordForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": _("Les deux mots de passe ne sont pas identiques"),
    }
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "


class CustomPasswordChangeForm(CustomSetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    error_messages = {
        **CustomSetPasswordForm.error_messages,
        "password_incorrect": _(
            "Votre ancien mot de passe est incorrect. Veuillez ressayer."
        ),
    }
    old_password = forms.CharField(
        label=_("Ancien mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


# ---------------------------------Authentication with Email Form-----------------------------------------#


class AuthenticationFormWithEmail(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Email ou mot de passe incorrect")
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError("Compte non activé")

    def get_user(self):
        return self.user_cache
