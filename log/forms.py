from django.forms import *
from django import forms
from datetime import datetime
from .models import *
from django.contrib.auth.forms import *

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

def str2season(string):
    return Season.objects.filter(start_date=string[:10])[0]

class SelectTimePeriodForm(forms.Form):
    seasons = []
    for season in Season.objects.all():
        start = season.start_date.strftime("%Y-%m-%d")
        end = season.end_date.strftime("%Y-%m-%d")
        seasons.append((season, start + " to " + end),)

    team = forms.ModelChoiceField(queryset=Team.objects.all(), label="Team")
    season = forms.TypedChoiceField(choices=seasons, coerce=str2season,
                                    label="Season")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(max_length=50, label="Password", widget=forms.PasswordInput)
