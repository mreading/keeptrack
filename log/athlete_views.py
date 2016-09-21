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
        return AddEventForm(request)

def get_form(run_type):
    if run_type == "normal":
        return AddNormalForm()
    elif run_type == "intervals":
        return AddIntervalForm()
    elif run_type == "xtrain":
        return AddXtrainForm()
    else:
        return AddEventForm()

def create_run(run_type, activity, data):
    if run_type == "normal":
        run = NormalRun.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration']
        )
    elif run_type == "intervals":
        pass
    elif run_type == "xtrain":
        run = CrossTrain.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['time'],
            sport=data['sport']
        )
    else:
        run = Event.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['time'],
            location=data['location'],
            place=data['place']
        )
    run.save()


def athlete(request):
    athlete = Athlete.objects.get(user=request.user)
    # print Coach.objects.get(user=request.user)

    activities = Activity.objects.filter(athlete=athlete).order_by('date')

    normal_runs = []
    for a in activities:
        normal_runs += NormalRun.objects.filter(activity=a)
    print normal_runs
    context = {
        'normal_runs':normal_runs
    }
    #------------------ mileage graph -----------------------

    #------------------ recent workouts ---------------------


    return render(request, "log/athlete.html", context)

def add(request, run_type):
    athlete = Athlete.objects.get(user=request.user)
    if request.method == 'POST':
        form = get_post_form(run_type, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            activity = Activity.objects.create(
                athlete=athlete,
                date=data['date'],
            )
            activity.save()
            create_run(run_type, activity, data)
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
