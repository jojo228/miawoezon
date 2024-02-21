# forms.py
from django import forms

from announcement.models import HouseType

class SearchForm(forms.Form):
    # Fields for Room model
    city = forms.CharField(required=False)
    guests = forms.IntegerField(required=False)
    check_in = forms.DateField(required=False)
    check_out = forms.DateField(required=False)
    
    # Fields for House model
    house_type = forms.ChoiceField(choices=HouseType, required=False)
    ville = forms.CharField(required=False)

