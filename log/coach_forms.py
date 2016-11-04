from django.forms import *
from django import forms
from .models import *
import datetime

YEARS = [('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')]
YEAR_CHOICES = ('2017', '2018', '2019', '2020')
GENDER_CHOICES = [('Men\'s', 'Men\'s'), ('Women\'s', 'Women\/s')]
SPORT_CHOICES = [('ITF', 'Indoor Track and Field'),
    ('OTF','Outdoor Track and Field'), ('XC', 'Cross Country')]

class NewSeasonForm(forms.Form):
    year = forms.IntegerField(
            widget=forms.Select(choices=YEARS), label = "Year")
    start_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "Start Date")
    end_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "End Date")


class NewTeamForm(forms.Form):
    sport = forms.CharField(
        widget=forms.Select(
            choices=SPORT_CHOICES), label = "Sport")
