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
            if user.is_authenticated:
                if user.is_active:
                    print "logging in!!!"
                    login(request, user)
                    return redirect("/log/")
                    if not request.POST.get('next'):
                        return redirect("/")
                    return redirect(request.POST.get('next'))
                else:
                    return HttpResponse("user not active")
            if 'token' in req.COOKIES:
                try:
                    invite = Invite.objects.get(cookie=req.COOKIES['token'])
                except Invite.DoesNotExist:
                    resp = redirect('/')
                    resp.delete_cookie('token')
                    return resp
                user = authenticate(username=invite.user.username, password='**')
            if user is None:
                return redirect('/')
            else:
                return HttpResponse("invalid login")

    return render(request, "log/login.html", {})

def logout_view(request):
    logout(request)
    return redirect('/log/login/')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a user
            user = User.objects.create_user(data['username'], data['email'], data['password'])
            user.first_name = data['first_name']
            user.last_name = data['last_name']

            # Create a team
            team = Team.objects.create(school_name = data['school'], gender = data['gender'], sport = data['sport'])

            # Create a coach
            coach = Coach.objects.create(user_id = user.id)
            coach.save()
            user.coach = coach
            coach.teams.add(team)

            # OLD CODE: used to be coach or athlete, now whoever is signing up
            # will be coach
            # Depending on whether the person signing up is a coach or an
            # athlete, different objects need to be created.
            # if data['is_coach'] == True:
            #     coach = Coach.objects.create(user_id = user.id)
            #     coach.save()
            #     user.coach = coach
            #     coach.teams.add(team)
            # else:
            #     print "was athlete"
            #     athlete = Athlete.objects.create(
            #         user_id=user.id,
            #         graduation_year=data['graduation_year'],
            #         #Probably other stuff here
            #         )
            #     athlete.save()
            #     user.athlete = athlete

            user.save()
            user = authenticate(username=data['username'], password=data['password'])
            login(request, user)
            return redirect("/log", {})
        else:
            return render(request, "log/signup.html", {'form':form})
    else:
        form = SignupForm()
        return render(request, "log/signup.html", {'form':form})

def AcceptInvite(request, key):
    return render(request, "log/settings.html", {})
