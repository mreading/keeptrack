from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .team_forms import *
from .utils import *
from .athlete_utils import *
from .team_views import get_team_season
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime
import json
from django.db.models import Q

def get_team_mileage_data(season):
    athletes = list(season.athlete_set.all())
    # 1. come up with an array of dates.
    today = datetime.date.today()
    start_week = today - datetime.timedelta(today.weekday())
    end_week = start_week + datetime.timedelta(7)

    curr_year = []
    curr_month = []
    curr_week = []
    curr_season = []

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

    # get the dates for the current week
    while start_week <= end_week:
        curr_week.append(start_week)
        start_week = start_week + datetime.timedelta(1)

    iter_date = season.start_date
    while iter_date < season.end_date:
        curr_season.append(iter_date)
        iter_date = iter_date + datetime.timedelta(1)

    # get the dates for the current season

    # 2. For that array, generate a new array of activites where the first element is
    # the date and the preceding elements are the number of miles an athlete ran on that day.

    # make labels
    data = [[a.user.last_name for a in athletes]]
    data[0].insert(0, 'Date')

    countable_run_types = ["NormalRun", "IntervalRun", "Event"]
    for d in curr_season:
        distances_for_day = [str(d)]
        for a in athletes:
            activities = list(Activity.objects.filter(
                date__year=d.year,
                date__month=d.month,
                date__day=d.day,
                athlete=a,
                # act_type__in=countable_run_types
            ))

            athlete_distance_for_day = 0
            for activity in activities:
                athlete_distance_for_day += get_miles(activity)

            distances_for_day.append(athlete_distance_for_day)

        data.append(distances_for_day)

    return data


def team_stats(request):
    user = request.user
    athlete = user.athlete_set.all()
    coach = user.coach_set.all()

    if coach:
        coach = coach[0]
        #Default to the current season
        if request.method == 'POST':
            form = SelectSeasonForm(request.POST, coach=coach)
            if form.is_valid():
                data = form.cleaned_data
                season = data['season']
                mileage_data = get_team_mileage_data(season)
                context = {
                    'form':form,
                    'mileage_data': json.dumps(mileage_data)
                }
                return render(request, "log/team_stats.html", context)
            else:
                print "form wasn't valid"

        #default to current season
        form = SelectSeasonForm(coach=coach)
        team, season = get_team_season(request.user)
        if season:
            data = get_team_mileage_data(season)
            context = {
                'form':form,
                'mileage_data':json.dumps(data)
            }
        else:
            context = {
                'form':form,
                'no_season':"No Current Season"
            }
        return render(request, "log/team_stats.html", context)

    else:
        print "Error: Athlete shouldn't be here"
        return render(request, "log/team_stats.html")
