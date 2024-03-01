from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import reverse_lazy
from authentication.forms import (
    CustomUserCreationForm,
    ClientPersonalDataForm,
    ClientAddressForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomPasswordChangeForm,
)

from authentication.forms import AuthenticationFormWithEmail
from . import views


app_name = "authentication"

urlpatterns = [
    # account
    path("<int:pk>", views.ClientDetailView.as_view(), name="client_detail"),
    path(
        "<int:pk>/identity_information/update",
        views.ClientIdentityInformationUpdateView.as_view(),
        name="client_identity_information_update",
    ),
    path(
        "<int:pk>/personal_information/update",
        views.ClientPersonalInformationUpdateView.as_view(),
        name="client_personal_information_update",
    ),
    path(
        "<int:pk>/address/update",
        views.ClientAddressUpdateView.as_view(),
        name="client_address_update",
    ),
    # signup
    path(
        "signup",
        views.SignupWizardView.as_view(
            [CustomUserCreationForm, ClientPersonalDataForm, ClientAddressForm]
        ),
        name="signup",
    ),
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),
    path("check-email/", views.CheckEmailView.as_view(), name="check_email"),
    path("success/", views.SuccessView.as_view(), name="success"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("main:home")),
        name="logout",
    ),
    # login
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            authentication_form=AuthenticationFormWithEmail,
            next_page=reverse_lazy("main:home"),
        ),
        name="login",
    ),
    # change password
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            form_class=CustomPasswordChangeForm,
            success_url=reverse_lazy("authentication:password_change_done"),
            template_name="password_change.html",
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="authentication/password_change_successful.html"
        ),
        name="password_change_done",
    ),
    # forgot password
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            email_template_name="authentication/password_reset_email.html",
            form_class=CustomPasswordResetForm,
            success_url=reverse_lazy("authentication:password_reset_done"),
            template_name="authentication/password_reset.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # reset password
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy("authentication:password_reset_complete"),
            template_name="authentication/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
