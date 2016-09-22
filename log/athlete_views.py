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

# def add_intervals(request):
#     # extra_reps = get_reps(request)
#     if request.method == 'POST':
#         extras = request.POST.get('extra_field_count')
#         print extras
#         form = AddIntervalForm(request.POST, extra=extras)
#         return render(request, "log/add_intervals.html", {'form':form})

        # if form.is_valid():
        #     for i in extras:
        #         print "HUH"
        #     return HttpResponse("Success!")
        # else:
        #     print "wasn't valid"
        #     print form.errors
    print "well here"
    form = AddIntervalForm()
    return render(request, "log/add_intervals.html", {'form':form})

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
    """
    Allows a user to update their own profile.
    """
    user = request.user

    # Create the formset, specifying the form and formset we want to use.
    AddRepFormSet = formset_factory(AddRepForm, formset=BaseAddRepFormSet)

    # Get our existing link data for this user.  This is used as initial data.
    # user_links = UserLink.objects.filter(user=user).order_by('anchor')
    # link_data = [{'anchor': l.anchor, 'url': l.url}
    #                 for l in user_links]

    if request.method == 'POST':
        IntervalForm = AddIntervalForm(request.POST, user=user)
        rep_formset = AddRepFormSet(request.POST)

        if IntervalForm.is_valid() and rep_formset.is_valid():
            # Save user info
            user.first_name = IntervalForm.cleaned_data.get('first_name')
            user.last_name = IntervalForm.cleaned_data.get('last_name')
            user.save()

            # Now save the data for each form in the formset
            new_links = []

            for rep_form in rep_formset:
                anchor = rep_form.cleaned_data.get('anchor')
                url = rep_form.cleaned_data.get('url')

            #     if anchor and url:
            #         new_links.append(UserLink(user=user, anchor=anchor, url=url))
            #
            # try:
            #     with transaction.atomic():
            #         #Replace the old with the new
            #         UserLink.objects.filter(user=user).delete()
            #         UserLink.objects.bulk_create(new_links)

                    # And notify our users that it worked
                    # messages.success(request, 'You have updated your profile.')

            # except IntegrityError: #If the transaction failed
            #     messages.error(request, 'There was an error saving your profile.')
            #     return redirect(reverse('profile-settings'))

    else:
        IntervalForm = AddIntervalForm(user=user)
        rep_formset = AddRepFormSet()

    context = {
        'IntervalForm': IntervalForm,
        'rep_formset': rep_formset,
    }

    return render(request, 'log/add_intervals.html', context)
