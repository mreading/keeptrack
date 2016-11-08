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
        seasons = kwargs.pop("seasons", None)
        super(SelectSeasonForm, self).__init__(*args, **kwargs)

        if seasons != None:
            self.fields['season'].queryset = seasons
