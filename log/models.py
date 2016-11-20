from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from datetime import date
from .utils import *
# from .athlete_utils import *

def get_workout_from_activity(activity):
    """---------------------------------------------------------
	  Given an activity, return the corrosponding run
	---------------------------------------------------------"""
    if activity.act_type == "NormalRun":
        return NormalRun.objects.get(activity=activity)
    if activity.act_type == "IntervalRun":
        return IntervalRun.objects.get(activity=activity)
    if activity.act_type == "CrossTrain":
        return CrossTrain.objects.get(activity=activity)
    if activity.act_type == "Event":
        return Event.objects.get(activity=activity)
    else:
        print "Unknown type of workout"

class Season(models.Model):
    """ ex: 2017 (athletes participate in seasons)"""
    #team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    start_date = models.DateField(default = date.today)
    end_date = models.DateField(default = date.today)

    def __str__(self):
        sport = self.team_set.all()[0].sport
        return sport + " " + self.start_date.strftime("%Y-%m-%d") + " to " + self.end_date.strftime("%Y-%m-%d")

class Team(models.Model):
    """ ex: Hamilton Men XC """
    school_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1)
    sport_choices = [
        ('Indoor Track and Field','ITF'),
        ('Outdoor Track and Field','OTF'),
        ('Cross Country','XC')
    ]
    sport = models.CharField(choices=sport_choices, max_length=3,
        default = 'Indoor Track and Field')
    seasons = models.ManyToManyField(Season)
    calendarId = models.CharField(max_length=200)

    #conference
    #mascot

    def __str__(self):
        return self.school_name + ' ' + self.gender + " " + self.sport

class Announcement(models.Model):
    text = models.CharField(max_length=2000)
    expiration_date = models.DateField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    posted_date = models.DateField()

class Athlete(models.Model):
    """ ex: Henry Whipple """
    seasons = models.ManyToManyField(Season)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graduation_year = models.PositiveIntegerField()
    log_private = models.BooleanField(default=True)
    default_location = models.CharField(max_length=50, default="Kirkland, NY")

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class Coach(models.Model):
    """ Brett Hull """
    teams = models.ManyToManyField(Team)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Shoe(models.Model):
    nickname = models.CharField(max_length=40)
    description = models.CharField(max_length=1000)
    athlete = models.ForeignKey(Athlete)
    miles = models.IntegerField(default=0)
    starting_mileage = models.IntegerField(default=0)
    def __str__(self):
        return self.nickname

    def update_miles(self):
        activities = list(Activity.objects.filter(
            act_type__in=['NormalRun', 'Event', 'IntervalRun'],
            shoe=self
        ))
        runs = []
        for a in activities:
            runs.append(get_workout_from_activity(a))

        self.miles = self.starting_mileage + sum([get_miles(r) for r in runs])

class Activity(models.Model):
    athlete = models.ForeignKey(Athlete)
    date = models.DateField()
    comment = models.CharField(max_length=1500, null=True)
    act_type = models.CharField(max_length=20, default='NormalRun')
    user_label = models.CharField(max_length=35, default="Normal Run")
    shoe = models.ForeignKey(Shoe, null=True)
    #weather
    #gpx file

    def __str__(self):
        return str(self.date) + ' ' + self.act_type

class Meet(models.Model):
    location = models.CharField(max_length=100)

class Event(models.Model):
    activity = models.ForeignKey(Activity)
    meet = models.ForeignKey(Meet)
    gender = models.CharField(max_length=1)
    distance = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    duration = models.DurationField()
    place = models.PositiveIntegerField()
    pace = models.DurationField(null=True)

    def __str__(self):
        return "{0} {1} race at {2}".format(
            str(self.distance),
            self.units[:-1],
            self.meet.location
        )

    def set_pace(self):
        num_miles = 0
        if self.units == 'Miles':
            num_miles = self.distance
        elif self.units == 'Kilometers':
            num_miles = kilometers_to_miles(self.distance)
        elif self.units == 'Meters':
            num_miles = kilometers_to_miles(self.distance)

        self.pace = timedelta(seconds=int(self.duration.total_seconds() / num_miles))

class NormalRun(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    duration = models.DurationField(null=True)
    pace = models.DurationField(null=True)
    #shoe
    #surface
    #route

    def __str__(self):
        return str(self.distance) + ' Mile Normal Run'

    def set_pace(self):
        num_miles = 0
        if self.units == 'Miles':
            num_miles = self.distance
        elif self.units == 'Kilometers':
            num_miles = kilometers_to_miles(self.distance)
        elif self.units == 'Meters':
            num_miles = kilometers_to_miles(self.distance)

        self.pace = timedelta(seconds=int(self.duration.total_seconds() / num_miles))

class CrossTrain(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    duration = models.DurationField()
    sport = models.CharField(max_length = 20)

    def __str__(self):
        return self.sport + ' (Cross training)' + ' for ' + str(self.duration)

class IntervalRun(models.Model):
    activity = models.ForeignKey(Activity)
    warmup = models.FloatField()
    cooldown = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    wu_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    cd_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    distance = models.FloatField(null=True)

    def __str__(self):
        return str(round(self.distance, 2)) + ' Mile Interval Run'

class Rep(models.Model):
    interval_run = models.ForeignKey(IntervalRun)
    distance = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    units = models.CharField(choices=unit_choices, default="Meters", max_length=12)
    duration = models.DurationField()
    goal_pace = models.FloatField(null=True)
    position = models.PositiveIntegerField()
    rest = models.DurationField(default=timedelta(seconds=1234))

class Thread(models.Model):
    activity = models.ForeignKey(Activity)

class Comment(models.Model):
    thread = models.ForeignKey(Thread)
    text = models.CharField(max_length=1500)
    position = models.IntegerField()
    private = models.BooleanField()
    poster = models.ForeignKey(User)

class Bug(models.Model):
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.description
