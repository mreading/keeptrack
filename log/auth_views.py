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
    return render(request, "log/logout.html", {})

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

def invite_render(req, tmpl="", data={}):
  return render_to_response(tmpl, data, context_instance=RequestContext(req))

def invite_user(req):
    # displays the InviteForm, and creates a user and an invite from the data.
    # Once the data has been created, an email is sent to the user who is being
    # invited.
    if req.method == 'POST':
        form = InviteForm(req.POST)
    if form.is_valid():
      user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], '**')
      user.first_name = form.cleaned_data['first_name']
      user.last_name = form.cleaned_data['last_name']
      user.is_active = False
      user.save()
      invite = Invite.objects.create(user=user, cookie='ck-test', token='tk-test')
      send_mail('Subject', 'Link: http://10.160.61.78:8001%s' % invite.get_absolute_url(), 'From', [user.email])
      return redirect('/')
    else:
        form = InviteForm()
    return invite_render(req, 'invite_form.html', {'form':form})

def confirm_invite(req, token):
    # used when a user clicks on the invitation link in their email.
    # Checks to see if the user is already active, so an invitation link cannot
    # be used twice, then it logs the user in. The middleware takes care of the
    # cookie creation for future logins.
    invite = get_object_or_404(Invite, token=token)
    user = invite.user
    if user.is_active == True:
        return redirect('/')
        user.is_active = True
    user.save()
    auth_user = authenticate(username=user.username, password='**')
    if auth_user is None:
        return redirect('/')
    login(req, auth_user)
    return redirect('/')
