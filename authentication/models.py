from django.db import models
from django.contrib.auth.models import User

User._meta.get_field('email')._unique = True



class Client(models.Model):
    MALE = "M"
    FEMALE = "F"
    SEX_CHOICES = [
        (MALE, "Masculin"),
        (FEMALE, "Féminin"),
    ]

    SINGLE = "S"
    DIVORCED = "D"
    MARRIED = "M"
    MATRIMONIAL_STATUS_CHOICES = [
        (SINGLE, "Célibataire"),
        (DIVORCED, "Marié.e"),
        (MARRIED, "Divorcé.e"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.BigIntegerField(null=True, blank=True)
    profession = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        null=True, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    matrimonial_status = models.CharField(
        max_length=1,
        choices=MATRIMONIAL_STATUS_CHOICES,
        null=True, blank=True
    )
    country = models.CharField(max_length=45,null=True, blank=True)
    city = models.CharField(max_length=200,null=True, blank=True)
    address = models.CharField(max_length=300,null=True, blank=True)
    pincode = models.CharField(max_length=20,null=True, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()



