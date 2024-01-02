from django.db import models
from enum import Enum
from django.urls import reverse



# Create your models here.

class HouseType(Enum):
    PIECE = "Pièce"
    DEUX_CHAMBRE_SALON = "Deux chambres salon"
    TROIS_CHAMBRE_SALON = "Trois chambres salon"
    VILLA = "Villa"
    MAISON = "Maison"
    APPARTEMENT = "Appartement"
    BUREAU = "Bureau"
    BOUTIQUE = "Boutique"
    APPARTEMENT_MEUBLES = "Appartement Meublé"
    TERRAINS_RURAUX = "Terrain Rural"



class Photo(models.Model):

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    house = models.ForeignKey("House", related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption
    


class House(models.Model):

    HOUSE_AVAILABILITY = [
        ("Disponible", "Disponible"),
        ("Non Disponible", "Non Disponible"),
    ]

    HOUSE_FOR = [
        ("Location", "Location"),
        ("Vente", "Vente"),
    ]


    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in HouseType])
    disponibilité = models.CharField(max_length=20, choices=HOUSE_AVAILABILITY,)
    pour = models.CharField(max_length=20, choices=HOUSE_FOR,)
    ville = models.CharField(max_length=80)
    prix = models.CharField(max_length=80)
    address = models.CharField(max_length=140)
    description = models.TextField()

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        self.ville = str.capitalize(self.ville)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def first_photo(self):
        try:
            (photo,) = self.photos.all()[:1]
            return photo.file.url
        except ValueError:
            return None

    def get_next_four_photos(self):
        photos = self.photos.all()[1:5]
        return photos