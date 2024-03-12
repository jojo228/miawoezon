from django import forms
from django_countries.fields import CountryField
from . import models


class SearchForm(forms.Form):

    city = forms.CharField(initial="Anywhere")
    country = CountryField(default="TG").formfield()
    room_type = forms.ModelChoiceField(
        required=False, empty_label="Any kind", queryset=models.RoomType.objects.all()
    )
    price = forms.IntegerField(required=False)
    guests = forms.IntegerField(required=False)
    bedrooms = forms.IntegerField(required=False)
    beds = forms.IntegerField(required=False)
    baths = forms.IntegerField(required=False)
    instant_book = forms.BooleanField(required=False)
    superhost = forms.BooleanField(required=False)
    amenities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    facilities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Facility.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ("caption", "file")

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()


class CreateRoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateRoomForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "
        
    class Meta:
        model = models.Room
        fields = (
            "name",
            "description",
            "country",
            "city",
            "price",
            "address",
            "guests",
            "beds",
            "bedrooms",
            "baths",
            "check_in",
            "check_out",
            "instant_book",
            "room_type",
            "amenities",
            "facilities",
            "house_rules",
            "video",
        )
        labels = {
            "name": "Titre",
            "description": "Description",
            "price": "Prix par nuit (xof)",
            "address": "Adresse",
            "guests": "Nombre d'invités autorisés",
            "amenities": "Commodités",
            "facilities": "Installations",
            "house_rules": "règles de la maison",
            "city": "ville",
            "beds": "Nombre de lits",
            "bedrooms": "chambres",
            "check_in": "Période d'entrée",
            "check_out": "Période de sortie",
            "room_type": "Type",
            "video": "Vidéo de presentation",
            "country": "Pays",
            "baths": "Douches",
            "instant_book": "Réservation instantanée",

        }

    
