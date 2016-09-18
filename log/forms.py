from django.forms import *
from django import forms
from .models import *

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(max_length=30, label="Password")
    email = forms.EmailField(max_length=100, label="Email")
    is_coach = forms.BooleanField(required=False, label="Are you a coach?")
    graduation_year = forms.IntegerField(label="Graduation Year")
