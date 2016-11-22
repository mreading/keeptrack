from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from .team_views import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required(login_url='/log/login/')
def help(request):
    return render(request, "log/help.html", {})

@login_required(login_url='/log/login/')
def index(request):
    if list(request.user.coach_set.all()):
        return team(request)
    else:
        return redirect("/log/athlete/"+str(request.user.id), {})

@login_required(login_url='/log/login/')
def settings(request):
    return render(request, "log/settings.html", {})

@login_required(login_url='/log/login/')
def submit_bug(request):
    bugs = Bug.objects.all()
    user = request.user
    if request.method == 'POST':
        # note the request.FILES parameter, an xml file of workout data
        form = AddBugForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            bug = Bug(description=data['description'])
            bug.save()
    form = AddBugForm()
    context = {
        'form':form,
        'bugs':bugs
    }
    return render(request, "log/bug_submission.html", context)

@login_required(login_url='/log/login/')
def delete_bug(request, bug_id):
    Bug.objects.get(pk=bug_id).delete()
    return redirect("/log/submit_bug/", {})
