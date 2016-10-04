from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .athlete_forms import *
from .utils import *
from .athlete_utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render
from .athlete_forms import AddRepForm, BaseAddRepFormSet, AddIntervalForm
import json

def athlete(request, user_id):
    # athlete = Athlete.objects.get(user=request.user)
    # print Coach.objects.get(user=request.user)
    user = User.objects.get(id=user_id)
    athlete = Athlete.objects.get(user=user)

    activities = Activity.objects.filter(athlete=athlete).order_by('date')

    all_runs = []
    for a in activities:
        all_runs += NormalRun.objects.filter(activity=a)
        all_runs += CrossTrain.objects.filter(activity=a)
        all_runs += IntervalRun.objects.filter(activity=a)
        all_runs += Event.objects.filter(activity=a)

    #------------------ mileage graph ----------------------
    runs = []
    for a in activities:
        runs += NormalRun.objects.filter(activity=a)
        runs += IntervalRun.objects.filter(activity=a)
        runs += Event.objects.filter(activity=a)

    # FIXME have to add colors for meets.
    colors = {
        'NormalRun':'#FFFFFF',
        'IntervalRun':'#CCCCCC',
    }

    mileage = []
    for run in runs:
        mileage.append([
            str(run.activity.date),
            run.distance,
            # colors[run.activity.act_type]
            # 'color: green'
            ])
    print mileage

    #------------------ recent workouts ---------------------

    context = {
        'all_runs':all_runs,
        'athlete':athlete,
        'athlete_user':user,
        'mileage':json.dumps(mileage)
    }

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
            thread = Thread.objects.create(activity=activity)
            thread.save()
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
    thread = Thread.objects.get(activity=activity)
    comments = Comment.objects.filter(thread=thread).order_by('position')
    reps = None
    if activity.act_type == 'NormalRun':
        workout = NormalRun.objects.get(activity=activity)
    elif activity.act_type == 'IntervalRun':
        workout = IntervalRun.objects.get(activity=activity)
        reps = Rep.objects.filter(interval_run=workout).order_by('position')
    elif activity.act_type == 'CrossTrain':
        workout = CrossTrain.objects.get(activity=activity)
    elif activity.act_type == 'Event':
        workout = Event.objects.get(activity=activity)


    if request.method == 'POST':
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            data = commentform.cleaned_data
            comment = Comment.objects.create(
                thread=thread,
                text=data['text'],
                private=False,
                position=len(Comment.objects.filter(thread=thread)),
                poster=request.user
                )
            comment.save()

    commentform = CommentForm()
    context = {
        'workout':workout,
        'activity':activity,
        'reps':reps,
        'commentform':commentform,
        'comments':comments
    }
    return render(request, "log/activity_detail.html", context)

def add_intervals(request):
    athlete = Athlete.objects.get(user=request.user)

    # Create the formset, specifying the form and formset we want to use.
    AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet)

    if request.method == 'POST':
        IntervalForm = AddIntervalForm(request.POST, user=request.user)
        rep_formset = AddRepFormSet(request.POST)

        if IntervalForm.is_valid() and rep_formset.is_valid():
            # Save Workout info
            interval_data = IntervalForm.cleaned_data

            #Create the Activity
            activity = Activity.objects.create(
                athlete=athlete,
                date=interval_data['date'],
                comment=interval_data['comments'],
                act_type='IntervalRun'
            )
            activity.save()
            thread = Thread.objects.create(activity=activity)
            thread.save()

            #Create the interval object
            interval_workout = IntervalRun.objects.create(
                activity=activity,
                warmup=float(interval_data['warmup']),
                wu_units=interval_data['wu_units'],
                cooldown=float(interval_data['cooldown']),
                cd_units=interval_data['cd_units'],
                total_distance=0.00
            )
            interval_workout.save()

            #create a number of reps for the inverval workout
            for i in range(len(rep_formset)):
                rep = Rep.objects.create(
                    interval_run=interval_workout,
                    distance=rep_formset[i].cleaned_data.get('rep_distance'),
                    units=rep_formset[i].cleaned_data.get('rep_units'),
                    duration=rep_formset[i].cleaned_data.get('rep_duration'),
                    rest=rep_formset[i].cleaned_data.get('rep_rest'),
                    position=i
                )
                rep.save()

            #Always assumed to be in miles
            set_total_distance(interval_workout)
            return redirect("/log/athlete", {})

    else:
        IntervalForm = AddIntervalForm(user=request.user)
        rep_formset = AddRepFormSet()

    context = {
        'IntervalForm': IntervalForm,
        'rep_formset': rep_formset,
    }

    return render(request, 'log/add_intervals.html', context)
