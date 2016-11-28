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

def get_team_season(user):
    if user.athlete_set.all():
        #get the athlete,
        athlete = list(user.athlete_set.all())[0]

        #then the season currently in session
        seasons = list(athlete.seasons.filter(
            start_date__lt=datetime.date.today(),
            end_date__gt=datetime.date.today()
        ))

        if len(seasons) == 0:
            seasons = list(athlete.seasons.all().order_by('-start_date'))

        if len(seasons) == 0:
            return None, None

        season = seasons[0]
        team = season.team_set.all()[0]
        return team, season

    else:
        # Get the coach associated with this user
        coach = list(user.coach_set.all())[0]

        # For each team associated with the
        for team in list(coach.teams.all()):
            seasons = list(team.seasons.filter(
                start_date__lt=datetime.date.today(),
                end_date__gt=datetime.date.today()
            ))
            if len(seasons) == 0:
                seasons = list(team.seasons.all().order_by('-start_date'))
            if len(seasons) != 0:
                return team, seasons[0]

        return None, None

    return None, None

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
            send_announcement(announcement.text, data['season'])
            return redirect("/log", {})
    return render(request, "log/announcement.html", {'form':form})

def get_recent_miles(athlete, days):
    activities = list(Activity.objects.filter(
        athlete=athlete,
        date__lt=datetime.date.today()+datetime.timedelta(1),
        date__gt=datetime.date.today()-datetime.timedelta(days),
        act_type__in=['NormalRun', 'Event', 'IntervalRun'],
    ))

    distance = sum([get_miles(get_workout_from_activity(a)) for a in activities])
    return distance

@login_required(login_url='/log/login')
def team(request):
    form = SelectTeamSeasonForm()
    if request.method == 'POST':
        form = SelectTeamSeasonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            team = data['team']
            season = data['season']
    else:
        team, season = get_team_season(request.user)

    if season == None:
        context = {
            'form':form,
            'no_season_alert': True
        }
        return render(request, "log/team.html", context)

    athletes = season.athlete_set.all()
    userIDs = []
    athleteData = []

    for athlete in athletes:
        row = [
            str(athlete.user.first_name),
            str(athlete.user.last_name),
            str(athlete.graduation_year),
            get_recent_miles(athlete, 7),
            get_recent_miles(athlete, 14),
            get_recent_miles(athlete, 30),
            ]
        userIDs.append(athlete.user.id)
        athleteData.append(row)


    announcements = Announcement.objects.filter(
        expiration_date__gt=datetime.date.today()
    )

    # getting calendar information for current week
    calendarId = team.calendarId
    #week = current_week(calendarId)
    week = [None]

    context = {
        'title': str(team),
        'form':form,
        'announcements':announcements,
        'athletes':athletes,
        'athleteData': athleteData,
        'userIDs':userIDs,
        'week': week
    }
    return render(request, "log/team.html", context)
