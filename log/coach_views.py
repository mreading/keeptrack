from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .coach_forms import *
from .forms import *
from .utils import *
from .calendar_views import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render, render_to_response
from invitations.models import Invitation
from django.db import IntegrityError
import datetime


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
            form = NewSeasonForm(request.POST, team = team)
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
                    existing_athletes = False;
                    team.seasons.add(season)
                    for team in coach.teams.all():
                        for temp_season in team.seasons.all():
                            if temp_season.athlete_set.count() != 0:
                                existing_athletes = True;
                                break;

                    if existing_athletes:
                        form = AddExistingAthleteForm(coach = coach)
                        return render(request, "log/add_existing_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season.id})
                    else:
                        form = AddAthleteForm()
                        return render(request, "log/add_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season.id})
                else:
                    return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team, 'season_aa': True})

            return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

        else:
            form = NewSeasonForm(team = team)
            return render(request, "log/create_season.html", {'form':form, 'coach': coach, 'team':team})

    elif athlete:
        return render(request, "log/settings.html")

    else:
        return render(request, "log/create_season.html")


def get_current_season(team):
    seasons = list(team.seasons.filter(
        start_date__lt=datetime.date.today(),
        end_date__gt=datetime.date.today()
    ))
    if len(seasons) == 0:
        seasons = team.seasons.order_by('start_date')

    if len(seasons) == 0:
        return None
    else:
        return seasons[0]

def existing_athletes(coach_id, season_id):
    coach = Coach.objects.filter(user=coach_id)[0]
    if coach:
        teams = coach.teams.all()
        athletes = Athlete.objects.none()

        for team in teams:
            seasons = team.seasons.all()
            for season in seasons:
                athletes = athletes | season.athlete_set.all()

        if season_id != 0:
            curr_season = Season.objects.filter(id = season_id)[0]
            athletes = athletes.exclude(pk__in = curr_season.athlete_set.all())
        athletes = list(athletes.distinct())
        return len(athletes) != 0


@login_required(login_url='/log/login/')
def manage_teams(request, user_id):

    user = User.objects.get(id=user_id)
    coach = user.coach_set.all()[0]
    teams = coach.teams.all()

    team_set = list()
    for team in teams:
        season = get_current_season(team)
        if season:
            season_id = season.id
        else:
            season_id = 0
        team_set.append((team, season, existing_athletes(user_id, season_id)))

    full_set = len(team_set) == 3

    return render(request, "log/manage_teams.html", {'user_id': user_id, 'team_set': team_set, 'coach': coach, 'full_team': full_set})

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

    if request.method == 'POST':
        form = NewTeamForm(request.POST, coach= coach)
        if form.is_valid():
            data = form.cleaned_data

            # Create a team, save it to the coach's teams
            if data['sport'] not in sport_list:

                # Create calendar for team
                #calendarId = create_calendar(school+" "+gender+" "+data['sport'])
                calendarId ="primary"

                # Share calendar with coach
                #share_calendar(calendarId, user.email)

                team = Team.objects.create(school_name = school, gender = gender, sport = data['sport'], calendarId=calendarId)
                coach.teams.add(team)
                return redirect("/log/manage_teams/" + str(user.id) + "/", {'full_team': len(sport_list) == 3})

            else:
                return render(request, "log/add_team.html", {'form':form})

        else:
            return render(request, "log/add_team.html", {'form':form})
    else:
        form = NewTeamForm(coach= coach)
        return render(request, "log/add_team.html", {'form':form})

@login_required(login_url='/log/login/')
def add_athletes(request, user_id, team_id, season_id):
    coach_user = User.objects.get(id=user_id)
    season = Season.objects.get(id = season_id)
    athletes = list(season.athlete_set.all())

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
                    "team_id": team_id, "season_id":season_id, 'athletes': athletes, 'existing_athletes': (len(athletes) != 0)})

            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()

            athlete = Athlete.objects.create(
                user_id=user.id,
                graduation_year=data['graduation_year'],
                phone_number=data['phone_number']
                )
            season = Season.objects.get(id = season_id)
            athlete.seasons.add(season)
            athlete.save()
            user.athlete = athlete

            # Notify the athlete that they have been added to keeptrack
            message = """Dear {0},

I have added you to our team's running log.

You can find it online at {1}. Your username/password are of the format 'DavidWippman/WippmanDavid' (Mind the capitalization and spacing!). \n\n

Please begin logging your mileage.

You can change the privacy settings (click on your name > settings). When your log is private, no one except your coach will be able to see your log. When it is public, it will show up with the other public logs on the team home page. You can change the privacy settings back and forth at your own will.

If you want to log a run via text message, simply text the number '12075170040' a message of the form <Ran 4.5 in h:m:s this is a comment> excluding the angle brackets. I recommend saving this number to your contacts, as you will be using it fairly often.

There are many other features that you should feel free to explore.

This website was built by Jack Pierce and his senior seminar group for computer science. If you have any issues or questions, either submit a bug using the link at the bottom of the page, or email him at jackhpierce@gmail.com.

Happy miles!""".format(user.first_name, "keeptrack.hamilton.edu/log/login/")
            send_mail(
                "Your Coach has added you to your team's running log",
                message,
                'keeptrack.hamilton@gmail.com',
                [user.email],
                fail_silently=False
            )

        else:
            return render(request, "log/add_athletes.html", {'form':form, 'coach': coach_user, "user_id": user_id,
            "team_id": team_id, "season_id":season_id, 'athletes': athletes, 'existing_athletes': (len(athletes) != 0)})

    form = AddAthleteForm()
    athletes = list(season.athlete_set.all())
    return render(request, "log/add_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season_id,'athletes': athletes, 'existing_athletes': (len(athletes) != 0)})

@login_required(login_url='/log/login/')
def add_coach(request, user_id):
    coach_user = User.objects.get(id=user_id)
    original_coach = coach_user.coach_set.all()[0]
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
                    'IE': True, "user_id": user_id})
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()

            coach = Coach.objects.create(
                user_id = user.id,
            )

            teams = original_coach.teams.all()
            for team in teams:
                coach.teams.add(team)

                # Share calendar with coach
                #share_calendar(team.calendarId, data['email'])
            coach.save()

            return redirect("/log/manage_teams/" + str(user_id) + "/", {})

        else:
            return render(request, "log/add_coach.html", {'form':form, 'user_id':user_id})

    form = AddCoachForm()
    return render(request, "log/add_coach.html", {'form':form, 'user_id':user_id})

def settings(request, user_id):
    coach = Coach.objects.filter(user=user_id)[0]
    return render(request, "log/coach_settings.html", {'user_id':user_id})

def all_seasons(request, team_id, user_id):
    team = Team.objects.filter(id=team_id)[0]
    # Sort seasons reverse chronologically
    seasons = team.seasons.order_by('-year')
    coach_set = team.coach_set.all()
    for coach_user in coach_set:
        coach = coach_user.user
    season_list = []
    for season in seasons:
         season_list.append((season, existing_athletes(coach.id, season.id)))
    return render(request, "log/all_seasons.html", {'user_id':user_id, 'team':team, 'seasons': season_list})

def add_existing_athletes(request, user_id, team_id, season_id):
    coach_user = User.objects.get(id=user_id)
    coach = Coach.objects.filter(user=user_id)[0]
    if request.method == 'POST':
        form = AddExistingAthleteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            season = Season.objects.get(id = season_id)
            for athlete in data['athletes']:
                athlete.seasons.add(season)

            return redirect("/log/manage_teams/" + str(user_id) + "/", {})

        else:
            return render(request, "log/add_existing_athletes.html", {'form':form, 'coach': coach_user, "user_id": user_id,
            "team_id": team_id, "season_id":season_id})

    form = AddExistingAthleteForm(season_id = season_id, coach = coach)
    return render(request, "log/add_existing_athletes.html", {'form': form, 'user_id': user_id, 'team_id': team_id, 'season_id': season_id})
