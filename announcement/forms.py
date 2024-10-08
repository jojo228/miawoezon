from django import forms
from django.core.exceptions import ValidationError
from announcement.models import House, Photo
from django.forms import modelformset_factory


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['file']

        
class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ("caption", "file")

        labels = {
            "caption": "Description",

        }

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        house = House.objects.get(pk=pk)
        photo.house = house
        photo.save()


class CreateHouseForm(forms.ModelForm):
        
    class Meta:
        model = House
        fields = (
            "type",
            "description",
            "disponibilité",
            "ville",
            "prix",
            "address",
            "caution",
            "pour",
        )
        labels = {
            "type": "Catégorie",
            "description": "Description",
            "prix": "Prix par mois (xof)",
            "address": "Adresse",
            "caution": "Caution (xof)",
            "ville": "Ville",
            "pour": "Pour",
            "disponibilité": "Disponibilité",

        }
    def __init__(self, *args, **kwargs):
        super(CreateHouseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "

    def clean_prix(self):
        prix = self.cleaned_data.get("prix")
        if not prix.isdigit():
            raise ValidationError("Prix must be a numeric value.")
        return prix
    
PhotoFormSet = modelformset_factory(Photo, fields=('file',), extra=5, can_delete=True)


class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Leave a comment!"}
        )
    )