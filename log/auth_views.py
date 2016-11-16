from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .calendar_views import *
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.messages import *
from django.contrib.auth.models import User
from django.db import IntegrityError


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_authenticated:
                    if user.is_active:
                        login(request, user)
                        return redirect("/log/")
                        if not request.POST.get('next'):
                            return redirect("/")
                        return redirect(request.POST.get('next'))
                    else:
                        return HttpResponse("user not active")

            else:
                return render(request, "log/login.html", {'form':form, 'wrong':True})
    else:
        form = LoginForm()
        return render(request, "log/login.html", {'form':form})

def logout_view(request):
    logout(request)
    return redirect('/log/login/')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a user
            try:
                user = User.objects.create_user(data['username'], data['email'], data['password'])
            except IntegrityError as e:
                return render(request, "log/signup.html", {'form':form,
                    'IE': True})
            user.first_name = data['first_name']
            user.last_name = data['last_name']

            # Create calendar for the team
            #calendarId = create_calendar(data['school']+" "+data['gender']+" "+data['sport'])
            calendarId = "primary"

            # Share calendar with coach
            #share_calendar(calendarId, data['email'])

            # Create a team
            team = Team.objects.create(school_name = data['school'], gender = data['gender'], sport = data['sport'], calendarId=calendarId)

            # Create a coach
            coach = Coach.objects.create(user_id = user.id)
            coach.save()
            user.coach = coach
            coach.teams.add(team)

            user.save()
            user = authenticate(username=data['username'], password=data['password'])
            login(request, user)
            return redirect("/log", {})
        else:
            return render(request, "log/signup.html", {'form':form})
    else:
        form = SignupForm()
        return render(request, "log/signup.html", {'form':form})

def change_password(request, user_id):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            data = form.cleaned_data
            return redirect("/log/", {})
        else:
            return render(request, "log/change_password.html", {'form':form, 'user_id':user_id})
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, "log/change_password.html", {'form':form, 'user_id':user_id})
