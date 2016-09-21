from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .athlete_forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def get_form(run_type, request):
    if run_type == "normal":
        return AddNormalForm(request)
    elif run_type == "intervals":
        return AddIntervalForm(request)
    elif run_type == "xtrain":
        return AddXtrainForm(request)
    else:
        return AddRaceForm(request)

def athlete(request):
    athlete = Athlete.objects.get(user=request.user)
    # print Coach.objects.get(user=request.user)

    activities = Activity.objects.filter(athlete=athlete)
    print activities
    #------------------ mileage graph -----------------------
    #------------------ recent workouts ---------------------

    return render(request, "log/athlete.html", {})

def add(request, run_type):
    if request.method == 'POST':
        form = get_form(run_type, request)
        if form.is_valid():
            data = form.cleaned_data
            #save the data
            return redirect("/log/athlete", {})
        else:
            return render(request, "log/add_run.html", {'form':form})

    form = get_form(run_type, request)
    return render(request, "log/add_run.html", {'form':form})
