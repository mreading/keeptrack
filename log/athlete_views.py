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
import datetime
from r2win_import import *

@login_required(login_url='/log/login/')
def delete_activity(request, activity_id):
    #make sure athlete is the one deleting the workout
    Activity.objects.get(id=activity_id).delete()
    return redirect("/log/athlete/"+str(request.user.id), {})

@login_required(login_url='/log/login/')
def edit_interval_run(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    i_run = IntervalRun.objects.get(activity=activity)
    reps = Rep.objects.filter(interval_run=i_run).order_by('position')

    if request.method == 'POST':
        IntervalForm = AddIntervalForm(request.POST)
        AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet)
        rep_formset = AddRepFormSet(request.POST)

        if IntervalForm.is_valid() and rep_formset.is_valid():
            # save the new data
            data = IntervalForm.cleaned_data
            i_run.warmup = float(data['warmup'])
            i_run.cooldown = float(data['cooldown'])
            i_run.cd_units = data['cd_units']
            i_run.save()

            activity.coment = data['comments']
            activity.date = data['date']
            activity.save()

            #the ordering of reps is probably messed up, so delete them all
            # and then create new rep objects
            Rep.objects.filter(interval_run=i_run).delete()
            for i in range(len(rep_formset)):
                rep = Rep.objects.create(
                    interval_run=i_run,
                    distance=float(rep_formset[i].cleaned_data.get('rep_distance')),
                    units=rep_formset[i].cleaned_data.get('rep_units'),
                    duration=rep_formset[i].cleaned_data.get('rep_duration'),
                    rest=rep_formset[i].cleaned_data.get('rep_rest'),
                    position=i
                )
                rep.save()

            # recalculate total distance of interval workout
            set_total_distance(i_run)
            i_run.save()
            return redirect("/log/athlete/"+str(request.user.id), {})

        else:
            print "invalid"
            context = {
                'IntervalForm':IntervalForm,
                'rep_formset':rep_formset,
                'activity':activity,
            }
            return render(request, "log/edit_run.html", context)

    #set initial interval form data
    IntervalForm = AddIntervalForm()
    IntervalForm.fields['warmup'].initial=i_run.warmup
    IntervalForm.fields['wu_units'].initial=i_run.wu_units
    IntervalForm.fields['cooldown'].initial=i_run.warmup
    IntervalForm.fields['cd_units'].initial=i_run.cd_units
    IntervalForm.fields['date'].initial=activity.date
    IntervalForm.fields['comments'].initial=activity.comment

    #set formset data
    AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet, min_num=0, extra=len(reps))
    rep_formset = AddRepFormSet()

    for i in range(len(reps)):
        rep_formset.forms[i].fields['rep_distance'].initial=reps[i].distance
        rep_formset.forms[i].fields['rep_units'].initial=reps[i].units
        rep_formset.forms[i].fields['rep_duration'].initial=reps[i].duration
        if reps[i].goal_pace != None:
            rep_formset.forms[i].fields['goal_pace'].initial=reps[i].goal_pace
        rep_formset.forms[i].fields['rep_rest'].initial=reps[i].rest

    print rep_formset.total_form_count()

    context = {
        'IntervalForm':IntervalForm,
        'rep_formset':rep_formset,
        'activity':activity,
    }

    return render(request, "log/edit_run.html", context)

@login_required(login_url='/log/login/')
def edit_xtrain(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    xtrain = CrossTrain.objects.get(activity=activity)

    if request.method == 'POST':
        form = AddXTrainForm(request.POST)
        if form.is_valid():
            # save the new data
            data = form.cleaned_data
            xtrain.distance=float(data['distance'])
            xtrain.duration=data['duration']
            xtrain.units=data['units']
            xtrain.sport=data['sport']
            activity.comment=data['comments']
            activity.date=data['date']
            activity.save()
            xtrain.save()
            return redirect("/log/athlete"+str(request.user.id), {})
    form = AddXTrainForm()
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=float(xtrain.distance)
    form.fields['units'].initial=xtrain.units
    form.fields['sport'].initial=xtrain.sport
    form.fields['duration'].initial=xtrain.duration
    form.fields['comments'].initial=activity.comment
    return render(request, "log/edit_run.html", {'form':form, 'activity':activity})

@login_required(login_url='/log/login/')
def edit_race(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    event = Event.objects.get(activity=activity)
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        if form.is_valid():
            # save the new data
            data = form.cleaned_data
            event.distance=float(data['distance'])
            event.duration=data['duration']
            event.units=data['units']
            event.gender=data['gender']
            event.meet.location=data['location']
            event.meet.save()
            activity.date=data['date']
            activity.comment=data['comments']
            activity.save()
            event.save()

            return redirect("/log/athlete/"+str(request.user.id), {})
    form = AddEventForm()
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=float(event.distance)
    form.fields['units'].initial=event.units
    form.fields['duration'].initial=event.duration
    form.fields['gender'].initial=event.gender
    form.fields['comments'].initial=activity.comment
    form.fields['location'].initial=event.meet.location
    form.fields['place'].initial=event.place
    return render(request, "log/edit_run.html", {'form':form, 'activity':activity})
    pass

@login_required(login_url='/log/login/')
def edit_normal(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    normal_run = NormalRun.objects.get(activity=activity)

    if request.method == 'POST':
        form = get_post_form(activity.act_type, request.POST)
        if form.is_valid():
            # save the new data
            data = form.cleaned_data
            normal_run.distance=float(data['distance'])
            normal_run.duration=data['duration']
            normal_run.units=data['units']
            activity.comment=data['comments']
            activity.date=data['date']
            activity.save()
            normal_run.save()
            return redirect("/log", {})
    form = get_form(activity.act_type)
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=normal_run.distance
    form.fields['units'].initial=normal_run.units
    form.fields['duration'].initial=normal_run.duration
    form.fields['comments'].initial=activity.comment
    return render(request, "log/edit_run.html", {'form':form, 'activity':activity})

#Redirects to aby of the five functions above depending on the type of activity
@login_required(login_url='/log/login/')
def edit_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    if activity.act_type == 'NormalRun':
        return edit_normal(request, activity_id)
    elif activity.act_type == 'IntervalRun':
        return edit_interval_run(request, activity_id)
    elif activity.act_type == 'CrossTrain':
        return edit_xtrain(request, activity_id)
    elif activity.act_type == 'Event':
        return edit_race(request, activity_id)

@login_required(login_url='/log/login/')
def athlete(request, user_id):

    user = User.objects.get(id=user_id)
    athlete = Athlete.objects.get(user=user)
    activities = Activity.objects.filter(athlete=athlete).order_by('date')

    #used for the list of recent activities
    all_runs = []
    for a in activities:
        all_runs += NormalRun.objects.filter(activity=a)
        all_runs += CrossTrain.objects.filter(activity=a)
        all_runs += IntervalRun.objects.filter(activity=a)
        all_runs += Event.objects.filter(activity=a)

    #------------------ mileage graph ----------------------
    #should also include days with no run...
    #Should have Year, Month, Week, Last 7 days, and Range

    #get run data
    runs = []
    for a in activities:
        runs += NormalRun.objects.filter(activity=a)
        runs += IntervalRun.objects.filter(activity=a)
        runs += Event.objects.filter(activity=a)

    year_activities = Activity.objects.filter(
        date__year=datetime.date.today().year,
        athlete=athlete
        ).order_by('date')
    year_activities = list(year_activities)

    month_activities = Activity.objects.filter(
        date__year=datetime.date.today().year,
        date__month=datetime.date.today().month,
        athlete=athlete
        ).order_by('date')
    month_activities = list(month_activities)

    # week_activities = Activity.objects.filter(
    #     date__year=datetime.date.today().year,
    #     date__month=datetime.date.today().month,
    #     date__week=datetime.date.today().week,
    #     athlete=athlete
    #     ).order_by('date')
    # week_activities = list(week_activities)

    # ------------------------- get dates -------------------------------------
    curr_year = []
    curr_month = []
    # curr_week = []

    jan_1st = datetime.date(year=datetime.date.today().year, month=1, day=1)
    dec_31st = datetime.date(year=datetime.date.today().year, month=12, day=31)

    #Get the dates for the current year
    iter_date = jan_1st
    while iter_date <= dec_31st:
        curr_year.append(iter_date)
        iter_date = iter_date + datetime.timedelta(1)

    #get the dates for the current month
    for day in curr_year:
        if day.month == datetime.date.today().month:
            curr_month.append(day)

    #get the dates for the current week
    # for i in range(7):
    #     curr_week.append(datetime.date.today() - datetime.timedelta(i))

    #--------------- generate graph data, including days off -------------------
    year_graph_data = build_graph_data(curr_year, year_activities)
    month_graph_data = build_graph_data(curr_month, month_activities)
    # week_graph_data = build_graph_data(curr_week, week_activities)
    #------------------ recent workouts ---------------------
    context = {
        'all_runs':all_runs,
        # 'year_graph_data':json.dumps(year_graph_data),
        # 'month_graph_data':json.dumps(month_graph_data),
        'athlete_user':user,
    }

    if request.method == 'POST':
        date_range_form = DateRangeForm(request.POST)
        if date_range_form.is_valid():
            #gett all dates between
            data = date_range_form.cleaned_data
            start_date = data['start_date']
            end_date = data['end_date']
            date_range = []
            for r in runs:
                if r.activity.date >= start_date and r.activity.date <= end_date:
                    date_range.append([
                        str(r.activity.date),
                        r.distance
                    ])
            context['date_range_mileage'] = date_range
            context['form'] = DateRangeForm()
            return render(request, "log/athlete.html", context)
    else:
        date_range_form = DateRangeForm()
        context['form'] = date_range_form

    return render(request, "log/athlete.html", context)

@login_required(login_url='/log/login/')
def add(request, run_type):
    if run_type == 'IntervalRun':
        add_intervals(request)
        return redirect("/log/athlete", {})

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
            return redirect("/log/athlete/"+str(request.user.id), {})
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

@login_required(login_url='/log/login/')
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

@login_required(login_url='/log/login/')
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
                distance=0.00
            )
            interval_workout.save()

            #create a number of reps for the inverval workout
            for i in range(len(rep_formset)):
                rep = Rep.objects.create(
                    interval_run=interval_workout,
                    distance=float(rep_formset[i].cleaned_data.get('rep_distance')),
                    units=rep_formset[i].cleaned_data.get('rep_units'),
                    duration=rep_formset[i].cleaned_data.get('rep_duration'),
                    rest=rep_formset[i].cleaned_data.get('rep_rest'),
                    position=i
                )
                rep.save()

            #Always assumed to be in miles
            set_total_distance(interval_workout)
            return redirect("/log/athlete/"+str(request.user.id), {})

    else:
        IntervalForm = AddIntervalForm(user=request.user)
        rep_formset = AddRepFormSet()

    context = {
        'IntervalForm': IntervalForm,
        'rep_formset': rep_formset,
    }

    return render(request, 'log/add_intervals.html', context)

@login_required(login_url='/log/login/')
def r2w_import(request):
    user = request.user
    athlete = Athlete.objects.get(user=user)
    if request.method == 'POST':
        form = R2WImportForm(request.POST, request.FILES)
        if form.is_valid():
            if len(request.FILES) != 0:
                f = request.FILES['log']
                import_from_file(f, athlete)
            return redirect("/log", {})
        else:
            return render(request, "log/r2w_import.html", {'form':form})
    else:
        form = R2WImportForm()
        return render(request, "log/r2w_import.html", {'form':form})
