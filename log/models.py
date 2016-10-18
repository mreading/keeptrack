from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from datetime import date

class Season(models.Model):
    """ ex: 2017 (athletes participate in seasons)"""
    #team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    start_date = models.DateField(default = date.today)
    end_date = models.DateField(default = date.today)

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

    #conference
    #mascot

    def __str__(self):
        return self.school_name + ' ' + self.gender + " " + self.sport


class Athlete(models.Model):
    """ ex: Henry Whipple """
    season = models.ManyToManyField(Season)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    graduation_year = models.PositiveIntegerField()

class Coach(models.Model):
    """ Brett Hull """
    teams = models.ManyToManyField(Team)
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
        return "{0} {1} race at {2}".format(
            str(self.distance),
            self.units[:-1],
            self.meet.location
        )

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
        return str(self.distance) + ' Mile Normal Run'

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

class Invite(models.Model):
    user = models.OneToOneField(User) # associated user with the invite.
    cookie = models.SlugField() # randomly generated string which is stored in the users browser.
    token = models.SlugField() # randomly generated string which is used in the invite URL
    def __unicode__(self):
        return u"%s %s's invite" % (self.user.first_name, self.user.last_name)

    @models.permalink
    def get_absolute_url(self):
        return ('invites.views.confirm_invite', [self.token])
