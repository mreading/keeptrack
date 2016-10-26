from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

# Google Calendar API modules
import httplib2
import os
import datetime
import pytz
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def print_10_events():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # change calendarId to pick calendar
    eventsResult = service.events().list(
        calendarId='esears@hamilton.edu', timeMin=now, maxResults=10,
        singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        #for key in event:
        #    print key, "=== ", event[key]
        #print
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def print_all_calendars():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # all user calendar
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print calendar_list_entry['summary']
            print calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

def create_calendar(name):
    # permissions only for viewing - not managing (FIX THIS)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar = {
    'summary': name,
    'timeZone': 'America/Los_Angeles'
    }

    new_calendar = service.calendars().insert(body=calendar).execute()
    return new_calendar['id']

def change_time(date, days=0, seconds=0, minutes=0, hours=0):
    # convert string to object
    timestamp = parse_datetime(date)

    # create change in time object
    deltatime = datetime.timedelta(days=days, seconds=seconds,
                                   minutes=minutes, hours=hours)

    # returns changed time in correct format
    return (timestamp + deltatime).isoformat()

def get_week(first, calendarId):
    # get google calendar information
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    start = first
    # get events for each day in the week
    week = [0,1,2,3,4,5,6]
    for day in week:
        # get end of the day timestamp
        finish = change_time(start, 1, -1)

        # get list of events for that day
        eventsResult = service.events().list(
            calendarId=calendarId, timeMin=start, timeMax=finish,
            singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        week[day] = events

        # start becomes beginning of next day
        start = change_time(start, 1)

    first = parse_datetime(first).strftime("%m/%d/%y")
    finish = parse_datetime(finish).strftime("%m/%d/%y")
    return [(first, finish), week]

def get_multiple_weeks(first_day, last_first_day, calendarId):
    weeks = []
    dates = []
    while first_day <= last_first_day:
        weeks.append(get_week(first_day, calendarId))
        first_day = change_time(first_day, 7)
    return weeks

def get_current_week(calendarId):
    # get current time with timezone
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(local_tz)

    # calculate start of the week (aka the first second of Monday)
    # now.weekday() gives a number where 0 is monday
    monday = change_time(now.isoformat(), -(now.weekday()))
    week_start = monday[:11] + "00:00:00" + monday[-6:]

    return get_week(week_start, calendarId)

def get_season_weeks(season, calendarId):
    # format start and end dates so they include time and timezones
    local_tz = pytz.timezone('US/Eastern')
    start = datetime.datetime.combine(season.start_date, datetime.time())
    start = timezone.make_aware(start, local_tz)
    finish = datetime.datetime.combine(season.end_date, datetime.time())
    finish = timezone.make_aware(finish, local_tz).isoformat()

    # make sure start is a monday
    start = change_time(start.isoformat(), -start.weekday())

    # get weeks for current season
    return get_multiple_weeks(start, finish, calendarId)

def get_current_team_season(seasons):
    # get current date and timezone
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now().date()

    # find the current season and team
    for season in seasons:
        if season.start_date <= now <= season.end_date:
            return season.team_set.all()[0], season

    # no current team/season
    return None, None

def get_teams_seasons(user_id):
    both = {}
    try: # Coach logged in
        # find all teams the coach controls
        teams = Coach.objects.get(user=user_id).teams.all()

        # get all seasons possible for each team
        seasons = []
        for team in teams:
            both[team] = team.seasons.all()
            seasons += team.seasons.all()

    except: # Atlete logged in
        # get all seasons athelete belongs to
        seasons = Athlete.objects.get(user=user_id).seasons.all()

        # find all teams the athlete is apart of based on seasons
        teams = []
        for season in seasons:
            teams.append(season.team_set.all()[0]) # only one team per season

        # get all seasons possible for each team
        seasons = []
        for team in teams:
            both[team] = team.seasons.all()
            seasons += team.seasons.all()

    return both, teams, seasons

@login_required(login_url='/log/login/')
def calendar(request):
    # get teams and seasons related to current user
    teams_seasons, teams, seasons = get_teams_seasons(request.user.id)

    # get the current season and team
    team, season = get_current_team_season(seasons)

    # no current team/season
    if not team:
        return render(request, "log/calendar.html",
                      {"weeks":[], "teams_seasons":teams_seasons})

    # needs to change based on team
    #calendarId = team.calendarId
    calendarId = 'primary'

    weeks = get_season_weeks(season, calendarId)
    return render(request, "log/calendar.html",
                  {"weeks":weeks, "teams_seasons":teams_seasons})

@login_required(login_url='/log/login/')
def time_period(request):
    if request.method == 'POST':
        form = SelectTimePeriodForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # CODE HERE
            team = data['team']
            season = data['season']

            # needs to change based on team
            #calendarId = team.calendarId
            calendarId = 'primary'

            weeks = get_season_weeks(season, calendarId)
            return render(request, "log/calendar.html",
                          {"weeks":weeks})
        else:
            return render(request, "log/select_time_period.html", {'form':form})
    else:
        form = SelectTimePeriodForm()
        return render(request, "log/select_time_period.html", {'form':form})
