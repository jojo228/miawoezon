from django.urls import path
from authentication.signup_views import signup, activate
from authentication.views import client_profil, login, password_reset_request, signout
from django.conf import settings
from django.conf.urls.static import static

app_name="authentication"

urlpatterns = [

    #Authentication urls
    path('login', login , name = 'login'),
    path('logout', signout , name = 'logout'),

    path('password_reset', password_reset_request, name='password_reset'),

    path('signup', signup , name = 'signup'),



    path('profil', client_profil, name='profil'),

    path('activate/<uidb64>/<token>', activate, name='activate'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
