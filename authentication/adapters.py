# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        # Redirect to the profile completion page after successful signup
        return reverse('authentication:complete_profile')
