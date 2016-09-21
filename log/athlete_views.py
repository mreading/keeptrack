from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def athlete(request):
    print Athlete.objects.get(user=request.user)
    # print Coach.objects.get(user=request.user)
    print "hello"
    return render(request, "log/athlete.html", {})
