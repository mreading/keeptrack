from django.forms import *
from django import forms
from .models import *
from datetime import date
from django.forms.formsets import BaseFormSet

class R2WImportForm(forms.Form):
    log = forms.FileField()

class DateRangeForm(forms.Form):
        start_date = forms.DateField(
            initial=date.today,
            widget=forms.widgets.DateInput(attrs={'type': 'date'})
            )
        end_date = forms.DateField(
            initial=date.today,
            widget=forms.widgets.DateInput(attrs={'type': 'date'})
            )

class SplitDurationWidget(forms.MultiWidget):
    """
    A Widget that splits duration input into four number input boxes.
    """
    def __init__(self, attrs=None):
        widgets = (forms.NumberInput(attrs=attrs),
                   forms.NumberInput(attrs=attrs),
                   forms.NumberInput(attrs=attrs),
                   forms.NumberInput(attrs=attrs))
        super(SplitDurationWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = value
            if d:
                hours = d.seconds // 3600
                minutes = (d.seconds % 3600) // 60
                seconds = d.seconds % 60
                return [int(d.days), int(hours), int(minutes), int(seconds)]
        return [0, 1, 0, 0]

class MultiValueDurationField(forms.MultiValueField):
    widget = SplitDurationWidget

    def __init__(self, *args, **kwargs):
        fields = (
         forms.IntegerField(),
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
                days=int(data_list[0]),
                hours=int(data_list[1]),
                minutes=int(data_list[2]),
                seconds=int(data_list[3]))
        else:
            return timedelta(0)

class AddNormalForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    distance = forms.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = forms.ChoiceField(choices=unit_choices)
    # duration = MultiValueDurationField()
    duration = DurationField()
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)

class AddXtrainForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )
    distance = forms.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers'),
        ('Laps', 'Laps'),
    ]
    units = forms.ChoiceField(choices=unit_choices)
    duration = forms.DurationField()
    sport = forms.CharField(max_length=20)
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)

class AddEventForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    distance = forms.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = forms.ChoiceField(choices=unit_choices)
    duration = forms.DurationField()
    location = forms.CharField(max_length=100)
    place = forms.IntegerField()
    comments = forms.CharField(max_length=1500,widget=forms.Textarea)


class AddRepForm(forms.Form):
    """
    Form for individual repeats
    """
    rep_distance = forms.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    rep_units = forms.ChoiceField(choices=unit_choices, initial='Meters')
    rep_duration = forms.DurationField()
    rep_rest = forms.DurationField()

class AddIntervalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        print "initializing interval form..."
        self.user = kwargs.pop('user', None)
        super(AddIntervalForm, self).__init__(*args, **kwargs)

        self.fields['warmup'] = forms.CharField()   #assumed to be in miles
        self.fields['cooldown'] = forms.CharField() #assumed to be in miles

        unit_choices = [
            ('Miles','Miles'),
            ('Meters','Meters'),
            ('Kilometers','Kilometers')
        ]
        self.fields['wu_units'] = forms.ChoiceField(
            choices=unit_choices,
            initial="Miles",
            )
        self.fields['cd_units'] = forms.ChoiceField(
            choices=unit_choices,
            initial="Miles",
            )

        self.fields['comments'] = forms.CharField(max_length=1500,widget=forms.Textarea)
        self.fields['date'] = forms.DateField(
            initial=date.today,
            widget=forms.widgets.DateInput(attrs={'type': 'date'})
        )

class BaseAddRepFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same rep_duration or rep_rest
        and that all links have both an rep_duration and rep_rest.
        """
        print "cleaning..."
        if any(self.errors):
            return
        print "here"
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

class CommentForm(forms.Form):
    text = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'style':'height: 30px; width: 100\%'}))
