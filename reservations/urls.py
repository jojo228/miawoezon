from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path(
        "create/<int:room>/",
        views.create,
        name="create",
    ),
    path("<int:pk>", views.ReservationDetailView.as_view(), name="detail"),
    path("<int:pk>/<str:verb>", views.edit_reservation, name="edit"),
    path("invoice/", views.invoice, name="invoice"),

    path('check-transaction/<str:transaction_id>/', views.check_transaction_by_id, name='check_transaction_by_id'),
    path('check-transaction/<str:token>/', views.check_transaction_by_token, name='check_transaction_by_token'),
]
