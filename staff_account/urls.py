from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from staff_account.forms import CustomStaffCreationForm
from staff_account.forms import StaffAddressForm, StaffPersonalDataForm
from authentication.forms import (
    CustomUserCreationForm,
    CustomPasswordChangeForm,
    AuthenticationFormWithEmail,
)
from . import views

app_name = "staff_account"

urlpatterns = [
    # staffs management
    # create
    path(
        "account/create",
        views.SignupWizardView.as_view(
            [CustomStaffCreationForm, StaffPersonalDataForm, StaffAddressForm]
        ),
        name="staff_account_create",
    ),
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),
    path("check-email/", views.CheckEmailView.as_view(), name="check_email"),
    path("success/", views.SuccessView.as_view(), name="success"),
    # list
    path("staff", views.StaffListView.as_view(), name="staff_account_list"),
    path("staff/list", views.StaffListView.as_view(), name="staff_account_list"),
    # read
    path(
        "staff/<int:pk>",
        views.StaffAccountDetailView.as_view(),
        name="staff_account_detail",
    ),
    path(
        "staff/detail/<int:pk>",
        views.StaffAccountDetailView.as_view(),
        name="staff_account_detail",
    ),
    # update
    path(
        "staff/update/<int:pk>/identity_information",
        views.StaffAccountIdentityInformationUpdateView.as_view(),
        name="staff_account_identity_information_update",
    ),
    path(
        "staff/update/<int:pk>/personal_information",
        views.StaffAccountPersonalInformationUpdateView.as_view(),
        name="staff_account_personal_information_update",
    ),
    path(
        "staff/update/<int:pk>/address",
        views.StaffAccountAddressUpdateView.as_view(),
        name="staff_account_address_update",
    ),
    # delete
    path(
        "staff/delete/<int:pk>",
        views.StaffAccountDeleteView.as_view(),
        name="staff_account_delete",
    ),
    # ----------------------------------------------------------------------------------------------------------------------#
    # staff
    # read
    path("<int:pk>", views.StaffDetailView.as_view(), name="staff_detail"),
    path("detail/<int:pk>", views.StaffDetailView.as_view(), name="staff_detail"),
    # update
    path(
        "update/<int:pk>/identity_information",
        views.StaffIdentityInformationUpdateView.as_view(),
        name="staff_identity_information_update",
    ),
    path(
        "update/<int:pk>/personal_information",
        views.StaffPersonalInformationUpdateView.as_view(),
        name="staff_personal_information_update",
    ),
    path(
        "update/<int:pk>/address",
        views.StaffAddressUpdateView.as_view(),
        name="staff_address_update",
    ),
    # logs
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("staff_account:login")),
        name="logout",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="staff_account/login.html",
            authentication_form=AuthenticationFormWithEmail,
            next_page=reverse_lazy("staff_section:project_list"),
        ),
        name="login",
    ),
    # change password
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            form_class=CustomPasswordChangeForm,
            template_name="staff_account/password_change.html",
            success_url=reverse_lazy("staff_account:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="staff_account/password_change_successful.html"
        ),
        name="password_change_done",
    ),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
