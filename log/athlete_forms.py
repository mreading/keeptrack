from django.forms import *
from django import forms
from .models import *
from datetime import date
from django.forms.formsets import BaseFormSet

class AddNormalForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    distance = forms.FloatField()
    duration = forms.DurationField()
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)

class AddIntervalForm(forms.Form):
    warm_up = forms.FloatField()
    cool_down = forms.FloatField()

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


class AddRepForm(forms.Form):
    """
    Form for individual user links
    """
    rep_duration = forms.FloatField(required=False)
    rep_rest = forms.DurationField(required=False)

class AddIntervalForm(forms.Form):
    """
    Form for user to update their own profile details
    (excluding links which are handled by a separate formset)
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddIntervalForm, self).__init__(*args, **kwargs)

        self.fields['warmup'] = forms.CharField()
        self.fields['cooldown'] = forms.CharField()

class BaseAddRepFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same rep_duration or rep_rest
        and that all links have both an rep_duration and rep_rest.
        """
        if any(self.errors):
            return

        rep_durations = []
        rep_rests = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                rep_duration = form.cleaned_data['rep_duration']
                rep_rest = form.cleaned_data['rep_rest']



                # Check that all links have both an rep_duration and rep_rest
                if rep_rest and not rep_duration:
                    raise forms.ValidationError(
                        'All links must have an rep_duration.',
                        code='missing_rep_duration'
                    )
                elif rep_duration and not rep_rest:
                    raise forms.ValidationError(
                        'All links must have a rep_rest.',
                        code='missing_rep_rest'
                    )
