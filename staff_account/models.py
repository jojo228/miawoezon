from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _

User._meta.get_field("email")._unique = True


# ------------------------------------------------------------------------#
# ------------------ Abstract Classes Definition -------------------------#
# ------------------------------------------------------------------------#

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

ALPHA = "A"
BETA = "B"
DELTA = "D"
GAMMA = "G"
POSITION_CHOICES = [
    (ALPHA, "Alpha"),
    (BETA, "Beta"),
    (DELTA, "Delta"),
    (GAMMA, "Gamma"),
]


class AccountCommonInfo(models.Model):

    LANGUAGE_ENGLISH = "en"
    LANGUAGE_FRENCH = "fr"

    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, _("English")),
        (LANGUAGE_FRENCH, _("French")),
    )

    CURRENCY_USD = "usd"
    CURRENCY_XOF = "xof"

    CURRENCY_CHOICES = (
        (CURRENCY_USD, "USD"),
        (CURRENCY_XOF, "XOF"),
    )

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "gmail"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Gmail"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.BigIntegerField(null=True)
    profession = models.CharField(max_length=200, null=True)
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        null=True
    )
    date_of_birth = models.DateField(null=True)
    matrimonial_status = models.CharField(
        max_length=1,
        choices=MATRIMONIAL_STATUS_CHOICES,
        null=True
    )
    country = models.CharField(max_length=45,null=True)
    city = models.CharField(max_length=200,null=True)
    address = models.CharField(max_length=300,null=True)
    pincode = models.CharField(max_length=20,null=True)
    date = models.DateTimeField(auto_now=True)

    language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=2, blank=True, default=LANGUAGE_FRENCH,null=True
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=3, blank=True, default=CURRENCY_XOF,null=True
    )

    class Meta:
        abstract = True



# ------------------------------------------------------------------------#
# ------------------ Abstract Classes Definition Ends --------------------#
# ------------------------------------------------------------------------#


# --------------------- About Staff -------------------------------------#


class Staff(AccountCommonInfo):
    position = models.CharField(max_length=200)

    def __str__(self):
        return self.user.get_full_name()
