from django.forms import *
from django import forms
from .models import *
from datetime import date

class AddNormalForm(forms.Form):
    date = forms.DateField(initial=date.today)
    distance = forms.FloatField()
    time = models.DurationField()

class AddIntervalForm(forms.Form):
    pass

class AddXtrainForm(forms.Form):
    date = forms.DateField()
    distance = forms.FloatField()
    time = forms.DurationField()
    sport = forms.CharField(max_length=20)

class AddRaceForm(forms.Form):
    date = forms.DateField()
    distance = forms.FloatField()
    time = forms.DurationField()
    location = forms.CharField(max_length=100)
    place = forms.IntegerField()
