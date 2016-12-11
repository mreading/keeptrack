from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from .athlete_forms import *
from .utils import *
from .athlete_utils import *
from .privacy import *
from r2win_import import *

import json
import datetime
import os

@login_required(login_url='/log/login')
def gear(request):
    if request.method == 'POST':
        form = ShoeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            shoe = Shoe.objects.create(
                nickname = data['nickname'],
                description = data['description'],
                athlete = request.user.athlete_set.all()[0],
                starting_mileage = data['starting_mileage']
            )
            shoe.save()
    shoes = list(request.user.athlete_set.all()[0].shoe_set.all())
    for shoe in shoes:
        shoe.update_miles()
    form = ShoeForm()
    athlete = Athlete.objects.get(user=request.user)
    context = wear_help(athlete.default_location)
    context['form'] = form
    context['shoes'] = shoes
    return render(request, 'log/gear.html', context)

@login_required(login_url='/log/login')
def range_select(request):
    if request.is_ajax() and request.method == "POST":
        context = {}
        date_range_form = DateRangeForm(request.POST)
        if date_range_form.is_valid():
            athlete = Athlete.objects.get(user=request.user)

            # get all dates between
            data = date_range_form.cleaned_data
            start_date = data['start_date']
            end_date = data['end_date']

            #collect all the dates between the start and the end date
            range_dates = [start_date]
            while range_dates[-1] <= end_date:
                range_dates.append(range_dates[-1]+datetime.timedelta(1))

            range_graph_data, range_total = build_graph_data(range_dates, athlete)
            return HttpResponse(json.dumps(range_graph_data))

    else:
        raise Http404

@login_required(login_url='/log/login/')
def wear(request):
    athlete = Athlete.objects.get(user=request.user)
    context = wear_help(athlete.default_location)
    return render(request, 'log/wear.html', context)

@login_required(login_url='/log/login/')
def delete_activity(request, activity_id):
    can_view, can_edit = athlete_privacy(request.user, Activity.objects.get(id=activity_id).athlete.user)
    if not can_edit:
        return HttpResponse("You are not allowed on this page")
    Activity.objects.get(id=activity_id).delete()
    return redirect("/log/athlete/"+str(request.user.id), {})

@login_required(login_url='/log/login/')
def edit_interval_run(request, activity_id):
    """---------------------------------------------------------
	  Given an activity's id, return the edit_run template with
      the correct form for the editing interval runs (and reps)
	---------------------------------------------------------"""
    activity = Activity.objects.get(id=activity_id)
    i_run = IntervalRun.objects.get(activity=activity)
    reps = Rep.objects.filter(interval_run=i_run).order_by('position')

    if request.method == 'POST':
        # Bind the POST data to the forms
        IntervalForm = AddIntervalForm(request.POST, user=activity.athlete.user)
        AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet)
        rep_formset = AddRepFormSet(request.POST)

        if IntervalForm.is_valid() and rep_formset.is_valid():
            # save the updated dated for both the interval run and the reps
            data = IntervalForm.cleaned_data
            i_run.warmup = float(data['warmup'])
            i_run.cooldown = float(data['cooldown'])
            i_run.cd_units = data['cd_units']
            i_run.save()
            activity.coment = data['comments']
            activity.date = data['date']
            activity.user_label=data['user_label']
            activity.shoe = data['shoe']
            activity.save()

            # The ordering of reps is probably messed up, so delete them all
            # and then create new rep objects rather than updating the existing
            # ones.
            Rep.objects.filter(interval_run=i_run).delete()
            for i in range(len(rep_formset)):
                rep = Rep.objects.create(
                    interval_run=i_run,
                    distance=round(float(rep_formset[i].cleaned_data.get('rep_distance')), 2),
                    units=rep_formset[i].cleaned_data.get('rep_units'),
                    duration=rep_formset[i].cleaned_data.get('duration'),
                    rest=rep_formset[i].cleaned_data.get('rep_rest'),
                    position=i+1 #not zero based
                )
                rep.save()

            # recalculate total distance of interval workout. If any of the
            # distances or numbers of the reps were edited than this total
            # distance for the run will be updated.
            set_total_distance(i_run)
            i_run.save()

            # redirect back to the athlete's home page
            return redirect("/log/athlete/"+str(request.user.id), {})

        else:
            # Form was not valid. Try again.
            context = {
                'IntervalForm':IntervalForm,
                'rep_formset':rep_formset,
                'activity':activity,
            }
            return render(request, "log/edit_run.html", context)

    # Set initial interval form data equal to what the run was previously
    IntervalForm = AddIntervalForm(user=activity.athlete.user)
    IntervalForm.fields['warmup'].initial=i_run.warmup
    IntervalForm.fields['wu_units'].initial=i_run.wu_units
    IntervalForm.fields['cooldown'].initial=i_run.cooldown
    IntervalForm.fields['cd_units'].initial=i_run.cd_units
    IntervalForm.fields['date'].initial=activity.date
    IntervalForm.fields['comments'].initial=activity.comment
    IntervalForm.fields['user_label'].initial=activity.user_label
    IntervalForm.fields['shoe'].initial=activity.shoe

    # Set the inital data for the formset just the same way as the previsou form
    AddRepFormSet = formset_factory(
        AddRepForm,
        formset=BaseAddRepFormSet,
        min_num=0,
        extra=len(reps) # need to keep the same number of reps
    )
    rep_formset = AddRepFormSet()
    for i in range(len(reps)):
        rep_formset.forms[i].fields['rep_distance'].initial=reps[i].distance
        rep_formset.forms[i].fields['rep_units'].initial=reps[i].units
        rep_formset.forms[i].fields['duration'].initial=reps[i].duration
        # Without the if statement an error is generated
        if reps[i].goal_pace != None:
            rep_formset.forms[i].fields['goal_pace'].initial=reps[i].goal_pace
        rep_formset.forms[i].fields['rep_rest'].initial=reps[i].rest

    # set the context dictionary to be rendered to the template
    context = {
        'IntervalForm':IntervalForm,
        'rep_formset':rep_formset,
        'activity':activity,
    }

    return render(request, "log/edit_run.html", context)

@login_required(login_url='/log/login/')
def edit_xtrain(request, activity_id):
    """---------------------------------------------------------
	  Given an activity's id, return the edit_run template with
      the correct form for the editing cross train runs
	---------------------------------------------------------"""
    activity = Activity.objects.get(id=activity_id)
    xtrain = CrossTrain.objects.get(activity=activity)

    if request.method == 'POST':
        # Bind the POST data to the form
        form = AddXTrainForm(request.POST, user=activity.athlete.user)
        if form.is_valid():
            # Save the updated data to CrossTrain object and the Activity Object
            data = form.cleaned_data
            data = form.cleaned_data
            xtrain.distance=round(float(data['distance']), 2)
            xtrain.duration=data['duration']
            xtrain.units=data['units']
            xtrain.sport=data['sport']
            activity.comment=data['comments']
            activity.date=data['date']
            activity.user_label=data['user_label']
            activity.shoe = data['shoe']
            activity.save()
            xtrain.save()
            return redirect("/log/athlete/"+str(request.user.id), {})

    # Bind the old data to the form so that it can be updated
    # NOTE for a modelform you could bind the data in one line, but
    # since this affects more than one object (ie Activity and CrossTrain) it
    # has to be done this way.
    form = AddXTrainForm(user=activity.athlete.user)
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=round(float(xtrain.distance), 2)
    form.fields['units'].initial=xtrain.units
    form.fields['sport'].initial=xtrain.sport
    form.fields['duration'].initial=xtrain.duration
    form.fields['comments'].initial=activity.comment
    form.fields['user_label'].initial=activity.user_label
    form.fields['shoe'].initial=activity.shoe

    context = {
        'form':form,
        'activity':activity
    }
    # render the template in context
    return render(request, "log/edit_run.html", context)

@login_required(login_url='/log/login/')
def edit_race(request, activity_id):
    """---------------------------------------------------------
	  Given an activity's id, return the edit_run template with
      the correct form for the editing races runs
	---------------------------------------------------------"""
    activity = Activity.objects.get(id=activity_id)
    event = Event.objects.get(activity=activity)
    if request.method == 'POST':
        form = AddEventForm(request.POST, user=activity.athlete.user)
        if form.is_valid():
            # save the new data
            data = form.cleaned_data
            event.distance=round(float(data['distance']), 2)
            event.duration=data['duration']
            event.units=data['units']
            event.gender=data['gender']
            event.meet.location=data['location']
            event.meet.save()
            activity.date=data['date']
            activity.comment=data['comments']
            activity.user_label=data['user_label']
            activity.shoe = data['shoe']
            activity.save()
            event.save()
            event.set_pace()
            # redirect back to the athlete's home page
            return redirect("/log/athlete/"+str(request.user.id), {})

    # Bind the old data to the form so that it can be updated
    # NOTE for a modelform you could bind the data in one line, but
    # since this affects more than one object (ie Activity and CrossTrain) it
    # has to be done this way.
    form = AddEventForm(user=activity.athlete.user)
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=round(float(event.distance), 2)
    form.fields['units'].initial=event.units
    form.fields['duration'].initial=event.duration
    form.fields['gender'].initial=event.gender
    form.fields['comments'].initial=activity.comment
    form.fields['location'].initial=event.meet.location
    form.fields['place'].initial=event.place
    form.fields['user_label'].initial=activity.user_label
    form.fields['shoe'].initial=activity.shoe

    #return the rendered template
    return render(request, "log/edit_run.html", {'form':form, 'activity':activity})

@login_required(login_url='/log/login/')
def edit_normal(request, activity_id):
    """---------------------------------------------------------
	  Given an activity's id, return the edit_run template with
      the correct form for the editing normal runs
	---------------------------------------------------------"""
    activity = Activity.objects.get(id=activity_id)
    normal_run = NormalRun.objects.get(activity=activity)

    if request.method == 'POST':
        form = get_post_form(activity.act_type, request.POST, activity.athlete.user)
        if form.is_valid():
            # save the updated data
            data = form.cleaned_data
            normal_run.distance=round(float(data['distance']), 2)
            normal_run.duration=data['duration']
            normal_run.units=data['units']
            activity.comment=data['comments']
            activity.date=data['date']
            activity.user_label=data['user_label']
            activity.shoe=data['shoe']
            activity.save()
            normal_run.set_pace()
            normal_run.save()
            return redirect("/log/athlete/"+str(request.user.id), {})
    # Bind the old data to the form for editing.
    form = get_form(activity.act_type, activity.athlete.user)
    form.fields['date'].initial=activity.date
    form.fields['distance'].initial=normal_run.distance
    form.fields['units'].initial=normal_run.units
    form.fields['duration'].initial=normal_run.duration
    form.fields['comments'].initial=activity.comment
    form.fields['user_label'].initial=activity.user_label
    form.fields['shoe'].initial=activity.shoe

    context = {
        'form':form,
        'activity':activity
    }
    return render(request, "log/edit_run.html", context)

@login_required(login_url='/log/login/')
def edit_activity(request, activity_id):
    """---------------------------------------------------------
	  Redirects to any of the five functions above depending
      on the type of activity
	---------------------------------------------------------"""
    can_view, can_edit = athlete_privacy(request.user, Activity.objects.get(id=activity_id).athlete.user)
    if not can_edit:
        return HttpResponse("You are not allowed on this page")

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
    """---------------------------------------------------------
	  This is the view that is the heart of the athlete page. It returns all
      the workout data for mileage graphs, for activities list, and for
      the upcoming races.
	---------------------------------------------------------"""
    # Locate the user, the athlete and the associated activities
    user = User.objects.get(id=user_id)
    athlete = Athlete.objects.get(user=user)

    #Make sure that if this log is private, only the athlete and the coach can see it
    can_view, can_edit = athlete_privacy(request.user, athlete.user)
    if not can_view:
        context = {
            'name':athlete.user.first_name
        }
        return render(request, "log/forbidden.html", context)

    all_runs = [get_workout_from_activity(a) for a in list(Activity.objects.filter(athlete=athlete).order_by('-date'))]

    #------------------ mileage graph ----------------------
    curr_year = []
    curr_month = []
    curr_week = []

    today = datetime.date.today()
    start_week = today - datetime.timedelta(today.weekday())
    end_week = start_week + datetime.timedelta(7)
    jan_1st = datetime.date(year=today.year, month=1, day=1)
    dec_31st = datetime.date(year=today.year, month=12, day=31)

    #Get the dates for the current year
    iter_date = jan_1st
    while iter_date <= dec_31st:
        curr_year.append(iter_date)
        iter_date = iter_date + datetime.timedelta(1)

    #get the dates for the current month
    for day in curr_year:
        if day.month == today.month:
            curr_month.append(day)

    # get the dates for the current week
    while start_week < end_week:
        curr_week.append(start_week)
        start_week = start_week + datetime.timedelta(1)

    #--------------- generate graph data, including days off -------------------
    year_graph_data, year_total = build_graph_data(curr_year, athlete)
    month_graph_data, month_total = build_graph_data(curr_month, athlete)
    week_graph_data, week_total = build_graph_data(curr_week, athlete)

    #------------------ Get PR's of athlete -----------------------------------
    prs = list(get_prs(athlete).values())

    # if len(all_runs) > 20:
    #     all_runs = all_runs[:19]

    context = {
        'can_edit':can_edit,
        'show_range_first':'false',
        'prs':prs,
        'all_runs':all_runs,
        'year_graph_data':json.dumps(year_graph_data),
        'year_total':year_total,
        'month_graph_data':json.dumps(month_graph_data),
        'month_total':month_total,
        'week_graph_data':json.dumps(week_graph_data),
        'week_total':week_total,
        'athlete_user':user,
    }

    context['form'] = DateRangeForm()

    return render(request, "log/athlete.html", context)

@login_required(login_url='/log/login/')
def add(request, run_type):
    """---------------------------------------------------------
	  Add a run with this view
	---------------------------------------------------------"""
    #This view only handles run addition for Races, Cross train,
    # and normal runs. Interval runs are complex and require their own view
    if run_type == 'IntervalRun':
        add_intervals(request)
        return redirect("/log/athlete", {})

    # Find the associated athlete
    athlete = Athlete.objects.get(user=request.user)
    if request.method == 'POST':
        # Get the right form for the run type
        form = get_post_form(str(run_type), request.POST, request.user)
        #validate the form
        if form.is_valid():
            # get the cleaned data (dictuonary form)
            data = form.cleaned_data
            # create an activity
            activity = Activity.objects.create(
                athlete=athlete,
                date=data['date'],
                act_type=run_type,
                comment=data['comments'],
                user_label=data['user_label'],
                shoe = data['shoe']
            )
            activity.save()
            # create an associated thread for comments
            thread = Thread.objects.create(activity=activity)
            thread.save()
            # create the associated run
            create_run(run_type, activity, data)
            return redirect("/log/athlete/"+str(request.user.id), {})

    # form has not been filled out yet. get the form and return it to the template
    form = get_form(run_type, request.user)
    context = {
        'form':form,
        'run_type':run_type
    }
    return render(request, "log/add_run.html", context)

@login_required(login_url='/log/login/')
def activity_detail(request, activity_id):
    """---------------------------------------------------------
	This is the view for showing the detail of a specific workout,
    Including comments, and ideally a graph of the intervals if the type
    is interval workout.
	---------------------------------------------------------"""
    activity = Activity.objects.get(id=activity_id)
    thread = Thread.objects.get(activity=activity)
    comments = Comment.objects.filter(thread=thread).order_by('position')
    reps = None
    interval_graph_data = None
    if activity.act_type == 'NormalRun':
        workout = NormalRun.objects.get(activity=activity)
    elif activity.act_type == 'IntervalRun':
        workout = IntervalRun.objects.get(activity=activity)
        reps = Rep.objects.filter(interval_run=workout).order_by('position')
        interval_graph_data = get_interval_graph_data(reps)
    elif activity.act_type == 'CrossTrain':
        workout = CrossTrain.objects.get(activity=activity)
    elif activity.act_type == 'Event':
        workout = Event.objects.get(activity=activity)

    # If comments were submitted, than they need to be saved and the page reloaded
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
            message = "{0} {1} Commented on your log! View comment here: {2}".format(
                comment.poster.first_name,
                comment.poster.last_name,
                "http://keeptrack.hamilton.edu/log/athlete/activity_detail/"+str(activity.id)
            )
            notify_these_people = [c.poster.email for c in list(Comment.objects.filter(thread=thread))] + [activity.athlete.user.email]
            # filter out duplicates
            notify_these_people = set(notify_these_people)
            # filter out current poster
            notify_these_people.remove(request.user.email)

            send_mail(
                'New Comment!',
                message,
                'keeptrack.hamilton@gmail.com',
                notify_these_people,
                fail_silently=False,
            )

    commentform = CommentForm()
    context = {
        'interval_graph_data':json.dumps(interval_graph_data),
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
                act_type='IntervalRun',
                user_label=interval_data['user_label'],
                shoe=interval_data['shoe']
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
                    distance=round(float(rep_formset[i].cleaned_data.get('rep_distance')), 2),
                    units=rep_formset[i].cleaned_data.get('rep_units'),
                    duration=rep_formset[i].cleaned_data.get('duration'),
                    rest=rep_formset[i].cleaned_data.get('rep_rest'),
                    position=i+1
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
    # This is the view for the Running2Win import.
    user = request.user
    athlete = Athlete.objects.get(user=user)
    if request.method == 'POST':
        # note the request.FILES parameter, an xml file of workout data
        form = R2WImportForm(request.POST, request.FILES)
        if form.is_valid():
            # if no file, do nothing.
            if len(request.FILES) != 0:
                f = request.FILES['log']
                # located in r2win_import.py
                import_from_file(f, athlete)
            return redirect("/log/athlete/"+str(request.user.id), {})

    form = R2WImportForm()
    return render(request, "log/r2w_import.html", {'form':form})

@login_required(login_url='/log/login/')
def settings(request, user_id):
    athlete = Athlete.objects.filter(user=user_id)[0]
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            athlete.log_private = data['log_private']
            athlete.default_location = data['default_location']
            athlete.save()
            return redirect("/log/athlete/{}/".format(athlete.user.id))
    form = SettingsForm()
    form.fields['log_private'].initial=athlete.log_private
    form.fields['default_location'].initial=athlete.default_location
    context = {
        'form':form
    }
    return render(request, "log/settings.html", context)
