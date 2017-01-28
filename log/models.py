from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from datetime import date
from .utils import *

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
        default = 'ITF')
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
    phone_number = models.CharField(max_length=11, null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class Coach(models.Model):
    """ Brett Hull """
    teams = models.ManyToManyField(Team)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

class Shoe(models.Model):
    nickname = models.CharField(max_length=40)
    description = models.CharField(max_length=1000)
    athlete = models.ForeignKey(Athlete)
    miles = models.IntegerField(default=0)
    starting_mileage = models.IntegerField(default=0)
    retired = models.BooleanField(default=False)
    def __str__(self):
        return self.nickname

    def update_miles(self):
        activities = list(Activity.objects.filter(
            act_type__in=['NormalRun', 'Event', 'IntervalRun'],
            shoe=self
        ))
        self.miles = self.starting_mileage + sum([get_miles(a) for a in activities])

class Meet(models.Model):
    location = models.CharField(max_length=100)

class Activity(models.Model):
    athlete = models.ForeignKey(Athlete)
    date = models.DateField()
    warmup = models.FloatField(default=0)
    cooldown = models.FloatField(default=0)
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    wu_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    cd_units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    sport = models.CharField(max_length=20, null=True)
    distance = models.FloatField(default=0)
    units = models.CharField(choices=unit_choices, default="Miles", max_length=12)
    unit_choices = [
        ('Miles','Miles'),
        ('Meters','Meters'),
        ('Kilometers','Kilometers')
    ]
    duration = models.DurationField(null=True)
    location = models.CharField(max_length=100, null=True)
    meet = models.ForeignKey(Meet, null=True)
    place = models.PositiveIntegerField(null=True)
    pace = models.DurationField(null=True)
    comment = models.CharField(max_length=3000, null=True)
    private_comments = models.CharField(max_length=2000, null=True)
    act_type = models.CharField(max_length=20, default='NormalRun')
    user_label = models.CharField(max_length=35, default="Normal Run")
    shoe = models.ForeignKey(Shoe, null=True)
    gender = models.CharField(max_length=10, default="M")

    def set_pace(self):
        num_miles = 0
        if self.units == 'Miles':
            num_miles = self.distance
        elif self.units == 'Kilometers':
            num_miles = kilometers_to_miles(self.distance)
        elif self.units == 'Meters':
            num_miles = kilometers_to_miles(self.distance)
        self.pace = timedelta(seconds=int(self.duration.total_seconds() / num_miles))

    def __str__(self):
        return str(self.date) + ' ' + self.act_type

class Rep(models.Model):
    activity = models.ForeignKey(Activity)
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
    rest = models.CharField(max_length=15, null=True)

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
