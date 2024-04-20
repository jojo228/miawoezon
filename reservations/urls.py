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

    # path('initialize-payment/', views.initiate_payment, name='initiate_payment'),
    # path('checkout/<int:payment_id>/', views.checkout, name='checkout'),
    path('handle-payment-return/', views.handle_payment_return, name='handle_payment_return'),
    path('handle-payment-notification/', views.handle_payment_notification, name='handle_payment_notification'),

    path("bookings/", views.bookings, name="bookings"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),
]
