from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone

class Athlete(models.Model):
    #using a foreign key is a little dangerous, but there isn't another option
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graduation_year = models.PositiveIntegerField()

class Coach(models.Model):
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

class NormalRun(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    time = models.DurationField
    #shoe
    #surface
    #route

class CrossTrain(models.Model):
    activity = models.ForeignKey(Activity)
    distance = models.FloatField()
    time = models.DurationField()
    sport = models.CharField(max_length = 20)


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
