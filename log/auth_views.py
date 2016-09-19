from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if not request.POST.get('next'):
                    return redirect("/log")
                return redirect(request.POST.get('next'))
            else:
                return HttpResponse("user not active")

        else:
            return HttpResponse("invalid login")
    return render(request, "log/login.html", {})

def logout_view(request):
    logout(request)
    return render(request, "log/logout.html", {})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(data['username'], data['email'], data['password'])
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
            return redirect("/log", {})
        else:
            return render(request, "log/signup.html", {'form':form})
    else:
        form = SignupForm()
        return render(request, "log/signup.html", {'form':form})
