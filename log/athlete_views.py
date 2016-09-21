from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .athlete_forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def get_post_form(run_type, request):
    if run_type == "normal":
        return AddNormalForm(request)
    elif run_type == "intervals":
        return AddIntervalForm(request)
    elif run_type == "xtrain":
        return AddXtrainForm(request)
    else:
        return AddRaceForm(request)

def get_form(run_type):
    if run_type == "normal":
        return AddNormalForm()
    elif run_type == "intervals":
        return AddIntervalForm()
    elif run_type == "xtrain":
        return AddXtrainForm()
    else:
        return AddRaceForm()

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
        form = get_form(run_type, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            #save the data
            return redirect("/log/athlete", {})
        else:
            context = {
                'form':form,
                'run_type':run_type
            }
            return render(request, "log/add_run.html", context)

    form = get_form(run_type)
    context = {
        'form':form,
        'run_type':run_type
    }
    return render(request, "log/add_run.html", context)
