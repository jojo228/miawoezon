from django.contrib.auth.backends import BaseBackend
from staff_account.models import User


class MyBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        try:
            email = kwargs["email"]
        except KeyError:
            return None
        password = kwargs["password"]
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) is True:
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, email):
        try:
            return User.objects.get(pk=email)
        except User.DoesNotExist:
            return None
