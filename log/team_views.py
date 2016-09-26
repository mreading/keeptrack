from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def team(request):
    athletes = Athlete.objects.all()
    print athletes
    print "hello"
    return render(request, "log/team.html", {'athletes':athletes})

def MyView(request):
    athletes=Athlete.objects.all()
    return render(request, "log/team.html", {'athletes':athletes})