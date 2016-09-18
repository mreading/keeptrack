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
