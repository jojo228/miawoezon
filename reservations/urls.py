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

    path('notify/', views.notification, name='notify'),
    path('initiate-transaction/<str:reservation_id>/', views.initiate_payment, name='initiate_transaction'),
    path('check-transaction/<str:transaction_id>/', views.check_transaction_by_id, name='check_transaction_by_id'),
    path('check-transaction/<str:token>/', views.check_transaction_by_token, name='check_transaction_by_token'),

    path("bookings/", views.bookings, name="bookings"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),
]
