from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .athlete_forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render
from .athlete_forms import AddRepForm, BaseAddRepFormSet, AddIntervalForm
# from myapp.models import UserLink

def get_post_form(run_type, request):
    if run_type == "NormalRun":
        return AddNormalForm(request)
    elif run_type == "IntervalRun":
        return AddIntervalForm(request)
    elif run_type == "CrossTrain":
        return AddXtrainForm(request)
    else:
        return AddEventForm(request)

def get_form(run_type):
    if run_type == "NormalRun":
        return AddNormalForm()
    elif run_type == "IntervalRun":
        return AddIntervalForm()
    elif run_type == "CrossTrain":
        return AddXtrainForm()
    else:
        return AddEventForm()

def create_run(run_type, activity, data):
    if run_type == "NormalRun":
        run = NormalRun.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration']
        )
    elif run_type == "IntervalRun":
        pass
    elif run_type == "CrossTrain":
        run = CrossTrain.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration'],
            sport=data['sport']
        )
    else:
        run = Event.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration'],
            location=data['location'],
            place=data['place']
        )
    run.save()

def athlete(request):
    athlete = Athlete.objects.get(user=request.user)
    # print Coach.objects.get(user=request.user)

    activities = Activity.objects.filter(athlete=athlete).order_by('date')

    all_runs = []
    for a in activities:
        all_runs += NormalRun.objects.filter(activity=a)
        all_runs += CrossTrain.objects.filter(activity=a)
        all_runs += IntervalRun.objects.filter(activity=a)
        all_runs += Event.objects.filter(activity=a)

    print all_runs
    context = {
        'all_runs':all_runs
    }
    #------------------ mileage graph -----------------------

    #------------------ recent workouts ---------------------


    return render(request, "log/athlete.html", context)

def add(request, run_type):
    if run_type == 'IntervalRun':
        add_intervals(request)
        return redirect("/log/athlete", {})

    print "RUN TYPE: "
    print run_type
    athlete = Athlete.objects.get(user=request.user)
    if request.method == 'POST':
        form = get_post_form(str(run_type), request.POST)
        if form.is_valid():
            data = form.cleaned_data
            activity = Activity.objects.create(
                athlete=athlete,
                date=data['date'],
                act_type=run_type,
                comment=data['comments']
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

def activity_detail(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    print activity.act_type
    reps = None
    if activity.act_type == 'NormalRun':
        workout = NormalRun.objects.get(activity=activity)
    elif activity.act_type == 'IntervalRun':
        workout = IntervalRun.objects.get(activity=activity)
        reps = Rep.objects.filter(IntervalRun=workout).order_by('position')
    elif activity.act_type == 'CrossTrain':
        workout = CrossTrain.objects.get(activity=activity)
    elif activity.act_type == 'Event':
        workout = Event.objects.get(activity=activity)

    context = {
        'workout':workout,
        'activity':activity,
        'reps':reps
    }
    return render(request, "log/activity_detail.html", context)

def add_intervals(request):
    athlete = Athlete.objects.get(user=request.user)
    
    # Create the formset, specifying the form and formset we want to use.
    AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet)

    if request.method == 'POST':
        IntervalForm = AddIntervalForm(request.POST, user=user)
        rep_formset = AddRepFormSet(request.POST)

        if IntervalForm.is_valid() and rep_formset.is_valid():
            # Save Workout info
            interval_data = IntervalForm.cleaned_data
            rep_data = rep_formset.cleaned_data

            print len(rep_formset)
            for rep_form in rep_formset:
                rep_duration = rep_form.cleaned_data.get('rep_duration')
                rep_rest = rep_form.cleaned_data.get('rep_rest')

                print rep_duration
                print rep_rest

            return redirect("/log/athlete", {})

    else:
        IntervalForm = AddIntervalForm(user=user)
        rep_formset = AddRepFormSet()

    context = {
        'IntervalForm': IntervalForm,
        'rep_formset': rep_formset,
    }

    return render(request, 'log/add_intervals.html', context)
