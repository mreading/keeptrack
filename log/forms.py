from django.forms import *
from django import forms
from datetime import datetime
from .models import *
from django.contrib.auth.forms import *
from django.forms import ModelChoiceField
from captcha.fields import CaptchaField


SPORT_CHOICES = [('ITF', 'Indoor Track and Field'),
    ('OTF','Outdoor Track and Field'), ('XC', 'Cross Country')]

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(max_length=30, label="Password", widget=forms.PasswordInput)
    email = forms.EmailField(max_length=100, label="Email")
    school = forms.CharField(max_length=50, label="School Name")

    gender = forms.CharField(
        widget=forms.Select(
             choices=[('Men\'s', 'Men\'s'), ('Women\'s', 'Women\'s')]), label="Team Gender")
    sport = forms.CharField(
        widget=forms.Select(
            choices=SPORT_CHOICES), label = "Sport")

    captcha = CaptchaField()

class AddAthleteForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    graduation_year = forms.IntegerField(label = "Graduation Year")
    email = forms.EmailField(max_length=100, label="Email")

class AddExistingAthleteForm(forms.Form):
    athletes = forms.ModelMultipleChoiceField(queryset=Athlete.objects.all(), label="Athletes") #to_field_name

    def __init__(self, *args, **kwargs):
        season_id = kwargs.pop('season_id', None)
        coach = kwargs.pop('coach', None)
        super(AddExistingAthleteForm, self).__init__(*args, **kwargs)

        if coach:
            teams = coach.teams.all()
            athletes = Athlete.objects.none()

            for team in teams:
                seasons = team.seasons.all()
                for season in seasons:
                    athletes = athletes | season.athlete_set.all()

            if season_id:
                curr_season = Season.objects.filter(id = season_id)[0]
                athletes = athletes.exclude(pk__in = curr_season.athlete_set.all())
            athletes = athletes.distinct()
            self.fields['athletes'].queryset = athletes

class AddCoachForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    email = forms.EmailField(max_length=100, label="Email")

class SelectTeamSeasonForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), label="Team")
    season = forms.ModelChoiceField(queryset=Season.objects.all(), label="Season")

    def __init__(self, *args, **kwargs):
        teams = kwargs.pop("teams", None)
        seasons = kwargs.pop("seasons", None)
        super(SelectTeamSeasonForm, self).__init__(*args, **kwargs)

        if teams != None:
            self.fields['team'].queryset = teams
            self.fields['season'].queryset = seasons

class SelectDateRangeForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), label="Team")
    start_date = forms.DateField(widget=forms.SelectDateWidget(), label="Start Date")
    end_date = forms.DateField(widget=forms.SelectDateWidget(), label="End Date")

    def __init__(self, *args, **kwargs):
        teams = kwargs.pop("teams", None)
        super(SelectDateRangeForm, self).__init__(*args, **kwargs)

        if teams != None:
            self.fields['team'].queryset = teams

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(max_length=50, label="Password", widget=forms.PasswordInput)

class AddBugForm(forms.Form):
    description = forms.CharField(max_length=1000, widget=Textarea)

class AddAnnouncementForm(forms.Form):
    text = forms.CharField(max_length=2000, widget=Textarea)
    expiration_date = forms.DateField(widget=forms.SelectDateWidget(), label="Expiration Date")
    season = forms.ModelChoiceField(queryset=Season.objects.all(),
        label="Season") #FIXME need to filter season options by teams that the coach coaches.
