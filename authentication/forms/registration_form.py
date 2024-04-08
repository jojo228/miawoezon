from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ValidationError

from authentication.models import Client


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(max_length=25 , required = True)

    class Meta:
        model = User
        fields = ['first_name'
         , 'last_name' , 'username'
          , "email" , 'password1'  , 'password2' ]
        
    def save(self, commit=True):
        user  = super(CreateUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
            
        if commit:
            user.save()
        return user



class EntrepriseUserForm(UserCreationForm):
    email = forms.EmailField(max_length=25 , required = True)

    class Meta:
        model = User
        fields = ['username'
          , "email" , 'password1'  , 'password2' ]
        
    def save(self, commit=True):
        user = super(EntrepriseUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
            
        if commit:
            user.save()
        return user

    

class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        exclude = ("user",)

