from django.forms import *
from django import forms
from .models import *
from datetime import date

class AddNormalForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    distance = forms.FloatField()
    duration = forms.DurationField()
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)

class AddIntervalForm(forms.Form):
    pass

class AddXtrainForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    distance = forms.FloatField()
    duration = forms.DurationField()
    sport = forms.CharField(max_length=20)
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)

class AddEventForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    distance = forms.FloatField()
    duration = forms.DurationField()
    location = forms.CharField(max_length=100)
    place = forms.IntegerField()
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)
