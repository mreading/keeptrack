from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Google Calendar API modules
import httplib2
import os
import datetime
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
            print calendar_list_entry
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

def create_calendar():
    # permissions only for viewing - not managing (FIX THIS)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar = {
    'summary': 'calendarSummary',
    'timeZone': 'America/Los_Angeles'
    }

    new_calendar = service.calendars().insert(body=calendar).execute()
    print new_calendar['id']

def change_time(date, days=0, seconds=0, minutes=0, hours=0):
    # convert string to object
    timestamp = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

    # create change in time object
    deltatime = datetime.timedelta(days=days, seconds=seconds,
                                   minutes=minutes, hours=hours)

    # returns changed time in correct format
    return (timestamp + deltatime).isoformat() + "Z"

def get_week(start):
    # get google calendar information
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # get events for each day in the week
    week = [0,1,2,3,4,5,6]
    for day in week:
        # get end of the day timestamp
        finish = change_time(start, 1, -1)

        # get list of events for that day
        eventsResult = service.events().list(
            calendarId='primary', timeMin=start, timeMax=finish,
            singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', ['summary'])
        week[day] = events

        # start becomes beginning of next day
        start = change_time(start, 1)

    return week

def get_multiple_weeks(first_day, last_first_day):
    weeks = []
    while first_day <= last_first_day:
        weeks.append(get_week(first_day))
        first_day = change_time(first_day, 7)
    return weeks

def get_current_week():
    # find monday start timestamp
    now = datetime.datetime.utcnow()
    day = now.weekday() # monday is 0
    week_start = change_time(now.isoformat()[:18]+"Z", -day)[:11] + "00:00:00Z"

    return get_week(week_start)

def calendar(request):
    #current = [get_current_week()]
    weeks = get_multiple_weeks("2016-10-17T00:00:00Z", "2016-11-21T00:00:00Z")
    return render(request, "log/calendar.html", {"weeks":weeks})
