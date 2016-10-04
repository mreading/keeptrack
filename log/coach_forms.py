from django.forms import *
from django import forms
from .models import *
import datetime


class NewTeamForm(forms.Form):
    school = forms.CharField(max_length=50, label="School")
    team = forms.CharField(max_length=50, label="Team")
    season = forms.CharField(max_length=50, label="Season")
    start_date = forms.DateField(initial=datetime.date.today, label = "Start Date")
    end_date = forms.DateField(initial=datetime.date.today, label = "End Date")

    """
    team = forms.IntegerField(
        widget=forms.Select(
            choices=Team.objects.all().values_list('id', 'school_name')
            )
         )
"""
