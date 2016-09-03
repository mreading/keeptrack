from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required(login_url='/log/login/')
def index(request):
    return render(request, "log/home.html", {})

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
