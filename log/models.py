from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone

class Team(models.Model):
    school_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1)
    #conference
    #mascot

    def __str__(self):
        return self.school_name + ' (' + self.gender + ')'

class Athlete(models.Model):
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
    #time
    #weather
    #gpx file

class Race(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    time = models.DurationField()
    location = models.CharField(max_length=100)
    place = models.PositiveIntegerField()

    def __str__(self):
        return 'Race at ' + self.location

class NormalRun(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    time = models.DurationField
    #shoe
    #surface
    #route

    def __str__(self):
        return str(self.distance) + ' mile run'

class CrossTrain(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    time = models.DurationField()
    sport = models.CharField(max_length = 20)

    def __str__(self):
        return self.sport + ' (Cross training)'

class IntervalRun(models.Model):
    activity = models.ForeignKey(Activity)
    warmup = models.FloatField()
    cooldown = models.FloatField()
    total_distance = models.FloatField()

class Rep(models.Model):
    interval_run = models.ForeignKey(IntervalRun)
    distance = models.FloatField()
    time = models.DurationField()
    goal_pace = models.FloatField()
    position = models.PositiveIntegerField()

class Thread(models.Model):
    activity = models.ForeignKey(Activity)

class Comment(models.Model):
    thread = models.ForeignKey(Thread)
    text = models.CharField(max_length=1500)
    position = models.IntegerField()
    private = models.BooleanField()
