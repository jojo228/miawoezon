from django import forms
from authentication.models import Client, User


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

        widgets = {
            "telephone": forms.NumberInput(attrs={"class": "form-control"}),
        }

        labels = {
            "telephone": "Téléphone",
        }


class ClientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

        labels = {
            "first_name": "Nom",
            "last_name": "Prénoms",
            "email": "Email",
        }
