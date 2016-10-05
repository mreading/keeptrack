from django.forms import *
from django import forms
from .models import *
import datetime

YEARS = [('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')]
YEAR_CHOICES = ('2017', '2018', '2019', '2020')
GENDER_CHOICES = [('Men\'s', 'Mens'), ('Women\'s', 'Womens')]
SPORT_CHOICES = [('ITF', 'ITF'), ('OTF','OTF'), ('XC', 'XC')]

class NewTeamForm(forms.Form):
    school = forms.CharField(
        widget=forms.Select(
            choices=Team.objects.all().values_list('id', 'school_name')), label = "School")
    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDER_CHOICES), label = "Gender")
    sport = forms.CharField(
        widget=forms.Select(
            choices=SPORT_CHOICES), label = "Sport")
    year = forms.IntegerField(
            widget=forms.Select(choices=YEARS), label = "Year")

    start_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "Start Date")

    end_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "End Date")
