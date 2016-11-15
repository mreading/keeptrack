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
    # year = forms.IntegerField(
    #         widget=forms.Select(choices=YEARS), label = "Year")
    # start_date = forms.DateField(
    #     widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "Start Date")
    # end_date = forms.DateField(
    #     widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "End Date")

    def __init__(self, *args, **kwargs):
        team = kwargs.pop("team", None)
        super(NewSeasonForm, self).__init__(*args, **kwargs)

        # Figure out which seasons already exist
        seasons = team.seasons.all()
        existing_seasons = []
        for season in seasons:
            existing_seasons.append(str(season.year))

        # Create a list of years up to four years from the current year, excluding the seasons that already exist
        current_year = datetime.date.today().year
        YEAR_CHOICES = []
        YEARS = []
        for i in range(4):
            if str(current_year) not in existing_seasons:
                YEAR_CHOICES.append(str(current_year))
                YEARS.append((str(current_year), str(current_year)))
            current_year = current_year + 1

        # Set the fields of the form
        self.fields['year'] = forms.IntegerField(
                widget=forms.Select(choices=YEARS), label = "Year")
        self.fields['start_date'] = forms.DateField(
            widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "Start Date")
        self.fields['end_date'] = forms.DateField(
            widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.date.today, label = "End Date")

class NewTeamForm(forms.Form):
    sport = forms.CharField(
        widget=forms.Select(
            choices=SPORT_CHOICES), label = "Sport")
