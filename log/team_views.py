"""---------------------------------------------------------------------------
 Imports
---------------------------------------------------------------------------"""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime

"""---------------------------------------------------------------------------
 Context created for team.html
---------------------------------------------------------------------------"""
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
            return redirect("/log", {})
    return render(request, "log/announcement.html", {'form':form})

def team(request):
    athletes = Athlete.objects.all()
    meets = Event.objects.all()
    userIDs = []
    athleteData = []
    meetData = []

    for meet in meets:
        row = [str(meet.meet.location), str(meet.activity.date), meet.distance, meet.place]
        meetData.append(row)

    for athlete in athletes:
        row = [str(athlete.user.first_name), str(athlete.user.last_name), str(athlete.graduation_year), 1]
        userIDs.append(athlete.user.id)
        athleteData.append(row)


    announcements = Announcement.objects.filter(
        expiration_date__gt=datetime.date.today()
    )

    context = {
        'announcements':announcements,
        'athletes':athletes,
        'athleteData': athleteData,
        'userIDs':userIDs,
        'meetData': meetData,
    }
    return render(request, "log/team.html", context)
