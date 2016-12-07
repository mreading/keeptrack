from django.forms import *
from django import forms
from .models import *
from datetime import date

class SelectSeasonForm(forms.Form):
    season = forms.ModelChoiceField(
        queryset=Season.objects.all(),
        label="Season"
    )

    def __init__(self, *args, **kwargs):
        coach = kwargs.pop("coach", None)
        super(SelectSeasonForm, self).__init__(*args, **kwargs)
        if coach != None:
            teams = coach.teams.all()
            seasons = Season.objects.filter(year=3000)
            for team in teams:
                seasons = seasons | team.seasons.all()
            self.fields['season'].queryset = seasons
