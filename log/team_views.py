"""---------------------------------------------------------------------------
 Imports
---------------------------------------------------------------------------"""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .athlete_utils import *
from .models import *
from .calendar_views import current_week
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime

def get_current_team_season(user):
    if user.athlete_set.all():
        #get the athlete,
        athlete = list(user.athlete_set.all())[0]
        print athlete
        #then the seasons that athlete has participated in,
        seasons = list(athlete.seasons.filter(
            start_date__lt=datetime.date.today(),
            end_date__gt=datetime.date.today()
        ))
        if len(seasons) == 0:
            season = athlete.seasons.order_by('start_date')[0]
        else:
            season = seasons[0]
        team = season.team_set.all()[0]

    else:
        coach = list(user.coach_set.all())[0]
        team = list(coach.teams.filter(sport='XC'))[0]
        seasons = list(team.seasons.filter(
            start_date__lt=datetime.date.today(),
            end_date__gt=datetime.date.today()
        ))
        if len(seasons) == 0:
            season = team.seasons.order_by('start_date')[0]
        else:
            season = seasons[0]

    return team, season

def create_announcement(request):
    try:
        coach = request.user.coach_set.all()[0]
    except:
        return HttpResponse("You are not a coach and therefore forbidden to post announcements")

    form = AddAnnouncementForm()
    if request.method == 'POST':
        form = AddAnnouncementForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            announcement = Announcement.objects.create(
                text = data['text'],
                expiration_date = data['expiration_date'],
                posted_date = datetime.date.today(),
                season = data['season'],
            )
            announcement.save()
            return redirect("/log", {})
    return render(request, "log/announcement.html", {'form':form})

def get_miles_last_7_days(athlete):
    activities = list(Activity.objects.filter(
        athlete=athlete,
        date__lt=datetime.date.today()+datetime.timedelta(1),
        date__gt=datetime.date.today()-datetime.timedelta(7),
        act_type__in=['NormalRun', 'Event', 'IntervalRun'],
    ))

    distance = sum([get_miles(get_workout_from_activity(a)) for a in activities])
    return distance

def team(request):
    form = SelectTeamSeasonForm()
    if request.method == 'POST':
        form = SelectTeamSeasonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            team = data['team']
            season = data['season']
    else:
        team, season = get_current_team_season(request.user)

    athletes = season.athlete_set.all()
    meets = Meet.objects.all()
    userIDs = []
    athleteData = []
    meetData = []

    for meet in meets:
        row = [str(meet.location)]
        meetData.append(row)

    for athlete in athletes:
        row = [
            str(athlete.user.first_name),
            str(athlete.user.last_name),
            str(athlete.graduation_year),
            get_miles_last_7_days(athlete)
            ]
        userIDs.append(athlete.user.id)
        athleteData.append(row)


    announcements = Announcement.objects.filter(
        expiration_date__gt=datetime.date.today()
    )

    # getting calendar information for current week
    #calendarId = team.calendarId
    calendarId = "primary"
    week = current_week(calendarId)

    print week

    context = {
        'title': str(team),
        'form':form,
        'announcements':announcements,
        'athletes':athletes,
        'athleteData': athleteData,
        'userIDs':userIDs,
        'meetData': meetData,
        'week': week
    }
    return render(request, "log/team.html", context)
