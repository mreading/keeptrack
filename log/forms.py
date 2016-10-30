from django.forms import *
from django import forms
from .models import *

SPORT_CHOICES = [('ITF', 'Indoor Track and Field'),
    ('OTF','Outdoor Track and Field'), ('XC', 'Cross Country')]

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(max_length=30, label="Password")
    email = forms.EmailField(max_length=100, label="Email")
    school = forms.CharField(max_length=50, label="School Name")
    gender = forms.CharField(
        widget=forms.Select(
             choices=[('Men\'s', 'Men\'s'), ('Women\'s', 'Women\'s')]), label="Team Gender")
    sport = forms.CharField(
        widget=forms.Select(
            choices=SPORT_CHOICES), label = "Sport")

class AddAthleteForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    graduation_year = forms.IntegerField(label = "Graduation Year")
    email = forms.EmailField(max_length=100, label="Email")

class AddCoachForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    email = forms.EmailField(max_length=100, label="Email")

class SelectTimePeriodForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), label="Team")
    season = forms.ModelChoiceField(queryset=Season.objects.all(), label="Season")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(max_length=50, label="Password", widget=forms.PasswordInput)
