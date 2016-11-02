from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .coach_forms import *
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render, render_to_response
from invitations.models import Invitation
from django.db import IntegrityError

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
                    team.seasons.add(season)
                    return redirect("/log/add_athletes/" + str(user.id) + "/" + str(team.id) + "/" + str(season.id) + "/", {})
                else:
                    return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

            return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

        else:
            form = NewSeasonForm()
            return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

    elif athlete:
        print "Error: Athlete shouldn't be here"
        return render(request, "log/settings.html")

    else:
        return render(request, "log/create_season.html")

@login_required(login_url='/log/login/')
def manage_teams(request, user_id):

    user = User.objects.get(id=user_id)
    coach = user.coach_set.all()[0]
    teams = coach.teams.all()

    return render(request, "log/manage_teams.html", {'user_id': user_id, 'teams': teams})

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
    coach_user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = AddAthleteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a user
            username = data['first_name'] + data['last_name']
            password = data['last_name'] + data['first_name']
            try:
                user = User.objects.create_user(username, data['email'], password)
            except IntegrityError as e:
                return render(request, "log/add_athletes.html", {'form':form,
                    'coach': coach_user, 'IE': True, "user_id": user_id,
                    "team_id": team_id, "season_id":season_id})

            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()

            athlete = Athlete.objects.create(
                user_id=user.id,
                graduation_year=data['graduation_year'],
                )
            season = Season.objects.get(id = season_id)
            athlete.seasons.add(season)

            athlete.save()
            user.athlete = athlete

        else:
            return render(request, "log/add_athletes.html", {'form':form, 'coach': coach_user, "user_id": user_id,
            "team_id": team_id, "season_id":season_id})

    form = AddAthleteForm()
    return render(request, "log/add_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season_id})

@login_required(login_url='/log/login/')
def add_coach(request, team_id):
    if request.method == 'POST':
        form = AddCoachForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a user
            username = data['first_name'] + data['last_name']
            password = data['last_name'] + data['first_name']
            try:
                user = User.objects.create_user(username, data['email'], password)
            except IntegrityError as e:
                return render(request, "log/add_coach.html", {'form':form,
                    'IE': True, "team_id": team_id})
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()

            # athlete = Athlete.objects.create(
            #     user_id=user.id,
            #     graduation_year=data['graduation_year'],
            #     #Probably other stuff here
            #     )

            coach = Coach.objects.create(
                user_id = user.id,
            )
            team = Team.objects.get(id=team_id)
            coach.teams.add(team)

            coach.save()

        else:
            return render(request, "log/add_coach.html", {'form':form, 'team_id':team_id})

    form = AddCoachForm()
    return render(request, "log/add_coach.html", {'form': form, 'team_id':team_id})

def settings(request, user_id):
    coach = Coach.objects.filter(user=user_id)[0]
    return render(request, "log/coach_settings.html", {'user_id':user_id})

def all_seasons(request, team_id, user_id):
    team = Team.objects.filter(id=team_id)[0]
    seasons = team.seasons.all()
    print seasons
    return render(request, "log/all_seasons.html", {'user_id':user_id, 'team':team, 'seasons': seasons})

def add_existing_athletes(request, user_id, team_id, season_id):
    coach_user = User.objects.get(id=user_id)
    coach = Coach.objects.filter(user=user_id)[0]
    if request.method == 'POST':
        form = AddExistingAthleteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            for athlete in data['athletes']:
                season = Season.objects.get(id = season_id)
                athlete.seasons.add(season)

            return redirect("/log/manage_teams/" + str(user_id) + "/", {})

        else:
            return render(request, "log/add_existing_athletes.html", {'form':form, 'coach': coach_user, "user_id": user_id,
            "team_id": team_id, "season_id":season_id})

    form = AddExistingAthleteForm(season_id = season_id, coach = coach)
    return render(request, "log/add_existing_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season_id})
