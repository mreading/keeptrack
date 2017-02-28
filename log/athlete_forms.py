#------------------------------------------------------------------------------
# PURPOSE: Form definitions used in athlete_views.py
# FILES: ./athlete_views.py
#------------------------------------------------------------------------------
from django.forms import *
from django import forms
from .models import *
from datetime import date
from django.forms.formsets import BaseFormSet

class ShoeForm(forms.Form):
    nickname = forms.CharField(max_length=50)
    description = forms.CharField(max_length=1000)
    starting_mileage = forms.IntegerField(initial=0)

class WearForm(forms.Form):
    town = forms.CharField(max_length=100, label="Town Name")
    state = forms.CharField(max_length=50, label="State Abbr")

class SettingsForm(forms.Form):
    log_private = forms.BooleanField(initial=False, required=False)
    default_location = forms.CharField(label="Default Location eg. Kirkland, NY")
    phone_number = forms.CharField(max_length=11, help_text="format: 12075530064")

class R2WImportForm(forms.Form):
    log = forms.FileField()

class DateRangeForm(forms.Form):
    """--------------------------------------------------------------------
    A form for getting a range of dates for mileage graphs
    --------------------------------------------------------------------"""
    start_date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    end_date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )

class SplitDurationWidget(forms.MultiWidget):
    """--------------------------------------------------------------------
    A Widget that splits duration input into four number input boxes.
    --------------------------------------------------------------------"""
    def __init__(self, attrs={'size':2}):
        widgets = (forms.TextInput(attrs=attrs),
                   forms.TextInput(attrs=attrs),
                   forms.TextInput(attrs=attrs),
                   forms.TextInput(attrs=attrs))
        super(SplitDurationWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = value
            if d:
                hours = d.seconds // 3600
                minutes = (d.seconds % 3600) // 60
                seconds = d.seconds % 60
                milliseconds = 0
                return [int(hours), int(minutes), int(seconds), int(milliseconds)]
        return [0, 0, 0, 0]

class MultiValueDurationField(forms.MultiValueField):
    widget = SplitDurationWidget

    def __init__(self, *args, **kwargs):
        fields = (
            #use a numberinput widget to set the width of the input fields
         forms.IntegerField(label="Hours"),
         forms.IntegerField(),
         forms.IntegerField(),
         forms.IntegerField(),
        )
        super(MultiValueDurationField, self).__init__(
            fields=fields,
            require_all_fields=True, *args, **kwargs
            )

    def compress(self, data_list):
        if len(data_list) == 4:
            return timedelta(
                hours=int(data_list[0]),
                minutes=int(data_list[1]),
                seconds=int(data_list[2]),
                milliseconds=int(data_list[3]) * 10
            )
        else:
            return timedelta(0)

class AddRepForm(forms.Form):
    """--------------------------------------------------------------------
    Form for individual repeats
    --------------------------------------------------------------------"""
    rep_distance = forms.FloatField(widget=TextInput(attrs={'size':4}), initial=0.0)
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    rep_units = forms.ChoiceField(choices=unit_choices, initial='Meters')
    duration = MultiValueDurationField(label="Duration (H:M:S:MS)")
    # goal_pace = forms.DurationField(optional=True)
    rep_rest = forms.CharField(max_length=15,widget=TextInput(attrs={'size':4}), required=True)

class AddActivityForm(forms.Form):
    activity_types = (
        ('-', '-'),
        ('NormalRun', 'Normal Run'),
        ('IntervalRun', 'Interval Run'),
        ('CrossTrain','Cross Train'),
        ('Event','Event')
    )
    act_type = forms.ChoiceField(choices=activity_types)
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    # Fields for Warmup/Cooldowns
    warmup = forms.FloatField(required=False, initial=0)
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    wu_units = forms.ChoiceField(
        choices=unit_choices,
        initial="Miles",
        required=False,
        label=""
    )
    cooldown = forms.FloatField(required=False, initial=0)
    cd_units = forms.ChoiceField(
        choices=unit_choices,
        initial="Miles",
        required=False,
        label=""
    )
    sport = forms.CharField(max_length=20,required=False)
    distance = forms.FloatField(initial=0, required=False)
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = forms.ChoiceField(choices=unit_choices, required=False)
    duration = MultiValueDurationField(label="Duration (Hour/Minute/Second/Millisecond)")
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)
    user_label = forms.CharField(max_length=35, initial="Normal Run")
    shoe = forms.ModelChoiceField(queryset=Shoe.objects.all(), required=False)

    # Fields for Race (Event)
    location = forms.CharField(max_length=100,required=False)
    place = forms.IntegerField(required=False, label="Finishing Place")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(AddActivityForm, self).__init__(*args, **kwargs)
        if user != None:
            athlete=Athlete.objects.get(user=user)
            self.fields['shoe'].queryset = Shoe.objects.filter(athlete=athlete)

class BaseAddRepFormSet(BaseFormSet):
    def clean(self):
        """--------------------------------------------------------------------
        Adds validation to check that no two links have the same duration or rep_rest
        and that all links have both an duration and rep_rest.
        --------------------------------------------------------------------"""
        if any(self.errors):
            return
        durations = []
        rep_rests = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                duration = form.cleaned_data['duration']
                rep_rest = form.cleaned_data['rep_rest']

                # Check that all links have both an duration and rep_rest
                if rep_rest and not duration:
                    raise forms.ValidationError(
                        'All links must have an duration.',
                        code='missing_duration'
                    )
                elif duration and not rep_rest:
                    raise forms.ValidationError(
                        'All links must have a rep_rest.',
                        code='missing_rep_rest'
                    )

class CommentForm(forms.Form):
    """--------------------------------------------------------------------
    Doesn't even need explaining
    --------------------------------------------------------------------"""
    text = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'style':'height: 30px; width: 100\%'}))
