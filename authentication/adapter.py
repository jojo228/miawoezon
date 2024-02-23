# adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.shortcuts import redirect

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Redirect to the profile completion page after successful signup
        return reverse('/authentication/complete_profile')
