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
def create_team(request, user_id):
    # Make sure user is coach
    user = User.objects.get(id=user_id)
    athlete = user.athlete_set.all()
    coach = user.coach_set.all()

    name = user.first_name

    if athlete:
        print("ATHLETE")
    if coach:
        print("COACH")
    else:
        print("NEITHER")

    # if user.athlete:
    #     print("USER.ATHLETE")
    # else:
    #     print("NO USER.ATHLETE")
    #
    # athlete = Athlete.objects.get(user=user)
    # #coach = Coach.objects.get(user=user)

    # if coach:
    #     print("COACH")
    # elif athlete:
    #     print("ATHLETE")
    # else:
    #     print("NEITHER COACH NOR ATHLETE")

    if request.method == 'POST':
        print("IN POST")
        form = NewTeamForm(request.POST)
        #if form.is_valid():
        #    data = form.cleaned_data
        if 0:


            """user = User.objects.create_user(data['username'], data['email'], data['password'])
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            team = Team.objects.get(id=int(data['team']))

            # Depending on whether the person signing up is a coach or an
            # athlete, different objects need to be created.
            if data['is_coach'] == True:
                print "was coach"
                coach = Coach.objects.create(user_id=user.id, team=team)
                user.coach = coach
            else:
                print "was athlete"
                athlete = Athlete.objects.create(
                    user_id=user.id,
                    graduation_year=data['graduation_year'],
                    team = team
                    #Probably other stuff here
                    )
                user.athlete = athlete

            user.save()
            user = authenticate(username=data['username'], password=data['password'])
            login(request, user)
            """
            return redirect("/log", {})
        else:
            return render(request, "log/create_team.html", {'form':form, 'user_id':user_id})

    else:
        form = NewTeamForm()
        return render(request, "log/create_team.html", {'form':form, 'user_id':user_id})
