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
    #Make sure user is coach
    user = User.objects.get(id=user_id)
    athlete = user.athlete_set.all()
    coach = user.coach_set.all()

    if coach:
        if request.method == 'POST':
            form = NewTeamForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                team = Team.objects.create(school_name = data['school'], gender = data['gender'])
                team.save()
                season = Season.objects.create(team = team, year = data['year'], sport = data['sport'])
                return redirect("/log", {})
            else:
                return render(request, "log/create_team.html", {'form':form})

        else:
            form = NewTeamForm()
            return render(request, "log/create_team.html", {'form':form})

    elif athlete:
        print "Athlete"
        return render(request, "log/settings.html")

    else:
        return render(request, "log/create_team.html")
