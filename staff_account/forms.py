from django import forms
from django.db.models import fields
from django.db.models.base import Model
from django.forms import ModelForm, widgets, SelectMultiple, RadioSelect
from .models import Staff
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm,
)
import unicodedata
from staff_account.models import User
from django.contrib.auth import authenticate


from django.utils.translation import gettext_lazy as _



# ---------------------------------Utilities classes-----------------------------------------------#


# staff creation account
class CustomStaffCreationForm(UserCreationForm):
    
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
        super(CustomStaffCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form__input"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "groups",
        )
        labels = {
            "first_name": "Prénom.s",
            "last_name": "Nom",
            "email": "Email",
            "groups": "Département",
        }
        widgets = {
            "groups": SelectMultiple(),
        }
        

# custom widget type for display date in html input date format
class DateInput(forms.DateInput):
    input_type = "date"


class StaffForm(ModelForm):
    class Meta:
        model = Staff
        exclude = ("user",)


class StaffIdentityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffIdentityForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form__input"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "groups")
        labels = {
            "first_name": "Prénom.s",
            "last_name": "Nom",
            "email": "Email",
            "groups": "Département",
        }


class StaffPersonalDataForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffPersonalDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form__input"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta:
        model = Staff
        fields = (
            "date_of_birth",
            "sex",
            "matrimonial_status",
            "contact",
            "profession",
            "position",
        )
        labels = {
            "date_of_birth": "Date de naissance",
            "sex": "Sexe",
            "matrimonial_status": "Statut Matrimonial",
            "profession": "Profession",
        }
        widgets = {"date_of_birth": DateInput()}


class StaffAddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffAddressForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form__input"
            visible.field.widget.attrs["placeholder"] = " "

    class Meta:
        model = Staff
        fields = (
            "country",
            "city",
            "address",
            "pincode",
        )
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
            visible.field.widget.attrs["class"] = "form__input"
            visible.field.widget.attrs["placeholder"] = " "
