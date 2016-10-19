"""---------------------------------------------------------------------------
 Imports
---------------------------------------------------------------------------"""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

"""---------------------------------------------------------------------------
 Context created for team.html
---------------------------------------------------------------------------"""
def team(request):
    athletes = Athlete.objects.all()
    meets = Event.objects.all()
    userIDs = []
    data1 = []
    for athlete in athletes:
        row = [str(athlete.user.first_name), str(athlete.user.last_name), str(athlete.graduation_year), 1]
        userIDs.append(athlete.user.id) 
        data1.append(row)
    return render(request, "log/team.html", {'athletes':athletes, 'meets':meets, 'data1': data1, 'userIDs':userIDs})