from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home , name="home"),
    path("search-results", views.search, name="search"),
    path("term_condition", views.term_condition , name="term_condition"),
    path("police_prive", views.police_prive , name="police_prive"),


    path("index2", views.index2 , name="index2"),
    path("index3", views.index3 , name="index3"),
    path("index4", views.index4 , name="index4"),
    path("coming-soon", views.coming_soon , name="coming-soon"),
    path("about", views.about , name="about"),
    path("contacts", views.contacts , name="contacts"),
    path("author-single", views.authorsingle , name="author-single"),
    path("help", views.help , name="help"),
    path("pricing-tables", views.pricingtables , name="pricing-tables"),
    path("booking-single", views.bookingsingle , name="booking-single"),
    path("dashboard", views.dashboard , name="dashboard"),
    path("blog2", views.blog2 , name="blog2"),
    path("blog-single", views.blogsingle , name="blog-single"),
    path("dashboard-add-listing", views.dashboardaddlisting , name="dashboard-add-listing"),
    path("error-page", views.errorpage , name="error-page"),
    path("invoice", views.invoice , name="invoice"),
    path("blog", views.blog , name="blog"),
    path("listing-single", views.listingsingle , name="listing-single"),
    path("listing-single2", views.listingsingle2 , name="listing-single2"),
    path("listing-single3", views.listingsingle3 , name="listing-single3"),
    path("listing-single4", views.listingsingle4 , name="listing-single4"),
    path("listing", views.listing, name="listing"),
    path("listing2", views.listing2, name="listing2"),
    path("listing3", views.listing3, name="listing3"),
    path("listing4", views.listing4, name="listing4"),
    path("listing6", views.listing6, name="listing6"),
    path("room1", views.room1, name="room1"),
    path("room2", views.room2, name="room2"),
    path("room3", views.room3, name="room3"),
    path("dashboard-listing-table", views.dashboardlistingtable , name="dashboard-listing-table"),
    path("dashboard-password", views.dashboardpassword, name="dashboard-password"),
    path("dashboard-review", views.dashboardreview , name="dashboard-review"),
    path("dashboard-add-listing", views.dashboardaddlisting , name="dashboard-add-listing"),









   






   
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)