from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from django.core import serializers
import simplejson as json

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

def create_calendar(name):
    # permissions only for viewing - not managing (FIX THIS)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar = {
    'summary': name,
    'timeZone': 'America/New_York'
    }

    new_calendar = service.calendars().insert(body=calendar).execute()
    return new_calendar['id']

def share_calendar(calendarId, email):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    rule = {
        'scope': {
            'type': 'user',
            'value': email,
        },
        'role': 'writer'
    }

    created_rule = service.acl().insert(calendarId=calendarId, body=rule).execute()

def remove_share(calendarId, email):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    service.acl().delete(calendarId=calendarId, ruleId="user:"+email).execute()

def change_time(date, days=0, seconds=0, minutes=0, hours=0):
    # convert string to object
    timestamp = parse_datetime(date)

    # create change in time object
    deltatime = datetime.timedelta(days=days, seconds=seconds,
                                   minutes=minutes, hours=hours)

    # returns changed time in correct format
    return (timestamp + deltatime).isoformat()

def sort_events(events, start, finish):
    weeks = []

    # time range for first day
    day_end = change_time(start, 1, -1)
    day_start = start

    # go through each day in the date range
    while day_start < finish:
        week = []
        week_range = [parse_datetime(day_start).strftime("%m/%d/%y"), None]

        # go through each day in a week
        for _ in range(7):
            day = []

            # go through each event and see if it is within the time range
            for i in range(len(events)):
                # get event start date/time
                try:
                    # event at certain time
                    current = events[i]['start']['dateTime']
                except:
                    # all day events so add time to date
                    current = events[i]['start']['date']
                    current = datetime.datetime.strptime(current, "%Y-%m-%d")
                    current = datetime.datetime.combine(current, datetime.time())
                    local_tz = pytz.timezone('US/Eastern')
                    current = timezone.make_aware(current, local_tz)
                    current = current.isoformat()

                # event is during the time range
                if day_start <= current <= day_end:
                    day.append(events[i])

                # event is after time range so stop looking through events
                elif day_end < current:
                    events = events[i:] # remove events already parsed
                    break

            # finished a day so add to week and increase time range
            week.append(day)
            day_start = change_time(day_start, 1)
            day_end = change_time(day_end, 1)

        # finished a week so add week and week range to weeks
        end_week = change_time(day_start, -1)
        week_range[1] = parse_datetime(end_week).strftime("%m/%d/%y")
        weeks.append([week_range, week])

    return weeks

def convert_start_end_dates(start, finish):
    # format start and end dates so they include time and timezones
    local_tz = pytz.timezone('US/Eastern')
    start = datetime.datetime.combine(start, datetime.time())
    start = timezone.make_aware(start, local_tz)
    finish = datetime.datetime.combine(finish, datetime.time())
    finish = timezone.make_aware(finish, local_tz)

    # make sure start is a monday and finish is a sunday
    start = change_time(start.isoformat(), -start.weekday())
    finish = change_time(finish.isoformat(), 7-finish.weekday(), -1)

    return start, finish

def range_weeks(start, finish, calendarId):
    # get google calendar information
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # get list of events within the date range
    eventsResult = service.events().list(
        calendarId=calendarId, timeMin=start, timeMax=finish,
        singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    # sort events into days and weeks
    # weeks is a list of weeks, week is a list of days, day is a list of events
    weeks = sort_events(events, start, finish)

    return weeks

def current_week(calendarId):
    # get current time with timezone
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(local_tz)

    # calculate start/end of the week
    # now.weekday() gives a number where 0 is monday
    monday = change_time(now.isoformat(), -(now.weekday()))
    week_start = monday[:11] + "00:00:00" + monday[-6:]
    week_end = change_time(week_start, 7, -1)

    return range_weeks(week_start, week_end, calendarId)[0]

def get_current_team_season(seasons):
    # get current date and timezone
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(local_tz).date()

    # find the current season and team
    for season in seasons:
        if season.start_date <= now <= season.end_date:
            return season.team_set.all()[0], season

    # no current team/season
    return None, None

def get_teams_seasons(user_id):
    try: # Coach logged in
        # find all teams the coach controls
        teams = Coach.objects.get(user=user_id).teams.all()

        # get all seasons possible for each team
        seasons = Season.objects.none()
        for team in teams:
            seasons = seasons | team.seasons.all()

    except: # Atlete logged in
        # get all seasons athelete belongs to
        seasons = Athlete.objects.get(user=user_id).seasons.all()

        # find all teams the athlete is apart of based on seasons
        teams = Team.objects.none()
        for season in seasons:
            teams = teams | season.team_set.all()

        # get rid of duplicates
        teams.distinct()

        # get all seasons possible for each team
        seasons = Season.objects.none()
        for team in teams:
            seasons = seasons | team.seasons.all()

    return teams, seasons

def get_ready_javascript(teams):
    t2s_map = {}
    for team in teams:
        t2s_map[team.__str__()] = serializers.serialize("json", team.seasons.all())

    return json.dumps(t2s_map)

@login_required(login_url='/log/login/')
def calendar(request):
    # get teams and seasons related to current user
    teams, seasons = get_teams_seasons(request.user.id)

    # get the current season and team
    team, season = get_current_team_season(seasons)

    # no current team/season
    if not team:
        return render(request, "log/calendar.html", {"weeks":[]})

    # needs to change based on team
    #calendarId = team.calendarId
    calendarId = 'primary'

    # convert season dates to datetimes
    start, finish = convert_start_end_dates(season.start_date, season.end_date)

    # get event data for season
    weeks = range_weeks(start, finish, calendarId)

    return render(request, "log/calendar.html", {"weeks":weeks})

@login_required(login_url='/log/login/')
def time_period(request):
    if request.method == 'POST':
        form = SelectDateRangeForm(request.POST)
        if form.is_valid():

            # get data from form
            data = form.cleaned_data
            start_date = data['start_date']
            end_date = data['end_date']

            # get start and end dates of season
            start, finish = convert_start_end_dates(start_date, end_date)

            # needs to change based on team
            #calendarId = team.calendarId
            calendarId = 'primary'

            weeks = range_weeks(start, finish, calendarId)
            return render(request, "log/calendar.html", {"weeks":weeks})
        else:
            return render(request, "log/select_time_period.html", {'form':form})
    else:
        form = SelectDateRangeForm()
        return render(request, "log/select_time_period.html", {'form':form})

@login_required(login_url='/log/login/')
def team_season(request):
    teams, seasons = get_teams_seasons(request.user.id)
    t2s_map = get_ready_javascript(teams)

    if request.method == 'POST':
        form = SelectTeamSeasonForm(request.POST)
        if form.is_valid():

            # get data from form
            data = form.cleaned_data
            team = data['team']
            season = data['season']

            # get start and end dates of season
            start, finish = convert_start_end_dates(season.start_date, season.end_date)

            # needs to change based on team
            #calendarId = team.calendarId
            calendarId = 'primary'

            weeks = range_weeks(start, finish, calendarId)
            return render(request, "log/calendar.html", {"weeks":weeks})
        else:
            return render(request, "log/select_time_period.html",
                {'form':form, 't2s_map':t2s_map, 'teams':teams})
    else:
        form = SelectTeamSeasonForm(teams=teams, seasons=seasons)
        return render(request, "log/select_team_season.html",
            {'form':form, 't2s_map':t2s_map, 'teams':teams})
