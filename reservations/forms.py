from django import forms
from . import models


class CreateRoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateRoomForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "custom-form"
            visible.field.widget.attrs["placeholder"] = " "
        
    class Meta:
        model = models.Reservation
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

    
