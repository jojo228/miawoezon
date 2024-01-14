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
    contact = models.BigIntegerField()
    profession = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to="avatars", blank=True)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
    )
    date_of_birth = models.DateField()
    matrimonial_status = models.CharField(
        max_length=1,
        choices=MATRIMONIAL_STATUS_CHOICES,
    )
    country = models.CharField(max_length=45)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    pincode = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now=True)

    language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=2, blank=True, default=LANGUAGE_FRENCH
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=3, blank=True, default=CURRENCY_XOF
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
