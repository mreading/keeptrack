from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .coach_forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render
import json

@login_required(login_url='/log/login/')
def create_season(request, user_id, team_id):
    #Make sure user is coach
    user = User.objects.get(id=user_id)
    team = Team.objects.get(id=team_id)
    athlete = user.athlete_set.all()
    coach = user.coach_set.all()

    if coach:
        coach = coach[0]
        print "COACH"
        print coach.teams.all()
        if request.method == 'POST':
            form = NewSeasonForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                # If season not already present, create season
                seasons = []
                for s in team.seasons.all():
                    seasons.append(s.year)

                if data['year'] not in seasons:
                    season = Season.objects.create(year = data['year'],
                        start_date = data['start_date'], end_date = data['end_date'])
                    season.save()
                    #season.team = team
                    team.seasons.add(season)
                    return redirect("/log/add_athletes/" + str(user.id) + "/" + str(team.id) + "/" + str(season.id) + "/", {})
                else:
                    return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})



            else:
                return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

        else:
            form = NewSeasonForm()
            return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

    elif athlete:
        print "Athlete"
        return render(request, "log/settings.html")

    else:
        return render(request, "log/create_season.html")

@login_required(login_url='/log/login/')
def manage_teams(request, user_id):

    user = User.objects.get(id=user_id)
    coach = user.coach_set.all()[0]
    teams = coach.teams.all()


    sport_list = []
    for team in teams:
        sport_list.append(team.sport)
    print sport_list

    return render(request, "log/manage_teams.html", {'teams': teams, 'full_team': len(sport_list) == 3})

@login_required(login_url='/log/login/')
def add_team(request, user_id):
    user = User.objects.get(id=user_id)
    coach = user.coach_set.all()[0]
    teams = coach.teams.all()
    school = teams[0].school_name
    gender = teams[0].gender

    sport_list = []
    for team in teams:
        sport_list.append(team.sport)
    print sport_list

    if request.method == 'POST':
        form = NewTeamForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a team, save it to the coach's teams
            if data['sport'] not in sport_list:
                print (data['sport'], "NOT IN sportlist")
                team = Team.objects.create(school_name = school, gender = gender, sport = data['sport'])
                coach.teams.add(team)
                return redirect("/log/manage_teams/" + str(user.id) + "/", {'full_team': len(sport_list) == 3})
            else:
                return render(request, "log/add_team.html", {'form':form})

        else:
            return render(request, "log/add_team.html", {'form':form})
    else:
        form = NewTeamForm()
        return render(request, "log/add_team.html", {'form':form})

@login_required(login_url='/log/login/')
def add_athletes(request, user_id, team_id, season_id):
    user = User.objects.get(id=user_id)
    return render(request, "log/add_athletes.html", {})
