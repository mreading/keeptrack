from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Team(models.Model):
    school_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1)
    #conference
    #mascot

    def __str__(self):
        return self.school_name + ' (' + self.gender + ')'

class Athlete(models.Model):
    #QUESTION: should we bulk this class up? Name,Status, etc? OR do we modularize?
    #using a foreign key is a little dangerous, but there isn't another option
    team = models.ForeignKey(Team)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graduation_year = models.PositiveIntegerField()

class Coach(models.Model):
    team = models.ForeignKey(Team)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Activity(models.Model):
    athlete = models.ForeignKey(Athlete)
    date = models.DateField()
    comment = models.CharField(max_length=1500, null=True)
    act_type = models.CharField(max_length=20, default='NormalRun')
    #duration
    #weather
    #gpx file

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

    def __str__(self):
        return 'Event at ' + self.location

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
    #shoe
    #surface
    #route

    def __str__(self):
        return str(self.distance) + ' mile run'

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
        return self.sport + ' (Cross training)'

class IntervalRun(models.Model):
    activity = models.ForeignKey(Activity)
    warmup = models.FloatField()
    cooldown = models.FloatField()
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    wu_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    cd_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    total_distance = models.FloatField()

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
