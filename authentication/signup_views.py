from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.forms.registration_form import ClientForm, CreateUserForm
from django.contrib.auth import login, get_user_model
from django.contrib.auth import login as auth_login
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .decorators import user_not_authenticated

from .tokens import account_activation_token


def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Cher {user}, Nous vous avons envoyé sur votre e-mail {to_email} des instructions pour activer votre compte. Si vous ne recevez pas de mail, veuillez vérifier vos spams.')
    else:
        messages.error(request, f'Problème d envoi de l e-mail de confirmation à {to_email}, vérifiez si vous l avez saisi correctement.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Merci pour votre confirmation. Vous pouvez maintenant vous connecter à votre compte.')
        return redirect('authentication:login')
    else:
        messages.error(request, 'Lien d Activation Invalide!')
    
    return redirect('main:home')



@user_not_authenticated
def signup(request):
    user_form = CreateUserForm()

    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        client_form = ClientForm(request.POST)
        if user_form.is_valid() and client_form.is_valid():
            user = user_form.save()
            client = client_form.save(commit=False)
            client.user = user
            client.save()
            # auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            activateEmail(request, user, user_form.cleaned_data.get('email'))
            username = user_form.cleaned_data.get('username')

            messages.success(request, 'Compte crée avec succès pour ' + username)
            return redirect("authentication:login")

    context = {'form':user_form}
    return render(request, 'signup.html', context)








