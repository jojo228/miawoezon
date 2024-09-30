from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path(
        "create/<int:room>/",
        views.CreateReservationView.as_view(),
        name="create",
    ),
    path("<int:pk>", views.ReservationDetailView.as_view(), name="detail"),
    path("<int:pk>/<str:verb>", views.edit_reservation, name="edit"),
    path("invoice/", views.invoice, name="invoice"),

    # Payment Successful
    path('payment/initialize/<int:pk>/', views.PaymentInitializationView.as_view(), name='payment_initialize'),
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    path('payment/return/', views.PaymentReturnView.as_view(), name='payment_return'),

    path("bookings/", views.bookings, name="bookings"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),
]
