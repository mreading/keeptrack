from twilio import twiml
from django_twilio.decorators import twilio_view
from django.http import HttpResponse
from .team_views import get_team_season
# include decompose in your views.py
from django_twilio.request import decompose
from log.models import *
import re
import datetime

def save_run(match, athlete):
    distance = match.group('distance')
    hours = match.group('hours')
    if hours == None:
        hours = 0
    minutes = match.group('minutes')
    seconds = match.group('seconds')
    comments = match.group('comments')

    activity = Activity.objects.create(
        athlete=athlete,
        date=datetime.date.today(),
        comment=comments,
        distance=float(distance),
        duration=datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds)),
        act_type="NormalRun"
    )
    activity.set_pace()
    activity.save()

    thread = Thread.objects.create(
        activity=activity
    )
    thread.save()

def generate_report(request):
    # Returns a string to send back to the athlete.
    report = ""
    athlete=Athlete.objects.get(user_id=request.user.id)
    today = datetime.date.today()
    athlete_activities = Activity.objects.filter(athlete=athlete)

    # last 7 days
    last_7 = athlete_activities.filter(
        date__gt=today - datetime.timedelta(7)
    )

    # current week
    start_week = today - datetime.timedelta(today.weekday())
    current_week = athlete_activities.filter(
        date__gte=start_week
    )

    # last_week
    last_week = athlete_activities.filter(
        date__lt=start_week,
        date__gte=start_week - datetime.timedelta(7)
    )
    # 2 weeks ago
    week_before = athlete_activities.filter(
        date__lt=start_week - datetime.timedelta(7),
        date__gte=start_week - datetime.timedelta(14)
    )

    last_7_total = sum([get_miles(a) for a in last_7])
    current_week_total = sum([get_miles(a) for a in current_week])
    last_week_total = sum([get_miles(a) for a in last_week])
    week_before_total = sum([get_miles(a) for a in week_before])

    # number of people who have logged runs on your team today, and collective number of miles
    team, season = get_team_season(athlete.user)

    athletes = season.athlete_set.all()
    total_miles_today = 0
    for a in athletes:
        acts = list(Activity.objects.filter(athlete=a, date=today))
        if len(acts) > 0:
            total_miles_today += sum([get_miles(act) for act in acts])

    # generate report strting
    report = "Last 7 Days: {0}\nThis Week: {1}\nLast Week: {2}\nWeek Before: {3}\n{4} teammate(s) logged {5} miles today.".format(
        round(last_7_total, 2),
        round(current_week_total, 2),
        round(last_week_total, 2),
        round(week_before_total, 2),
        len(Activity.objects.filter(date=datetime.date.today(), athlete__in=athletes).values('athlete').distinct()),
        round(total_miles_today, 2)
    )
    return report

def process_sms_text(text, from_num):
    athlete_queryset = Athlete.objects.filter(phone_number=from_num[1:])
    # Make sure the athlete exists in the database
    if len(lst(athlete_queryset)) == 0:
        return "This number is not known by KeepTrack. Change it in settings"
    else:
        athlete = athlete_queryset[0]

    # Athlete is trying to save a run
    exp = r'^(r|R)an (?P<distance>[0-9]+(\.[0-9]+)?)\s*in ((?P<hours>[0-9]*):)?(?P<minutes>[0-9]+):(?P<seconds>[0-9]+) (?P<comments>.*)'
    match = re.search(exp, text)
    if match:
        save_run(match, athlete)
        return "Your run has been saved!"

    exp = r'(r|R)eport'
    match = re.search(exp, text)
    if match:
        return generate_report(athlete)



@twilio_view
def inbound(request):
    response = twiml.Response()
    # Create a new TwilioRequest object
    twilio_request = decompose(request)

    # Capture the sender and the text
    from_num = str(twilio_request.from_)
    text = str(twilio_request.body)

    # Process the text
    result = process_sms_text(text, from_num)

    # Return a response text to the user
    if not result:
        if twilio_request.type is 'message':
            response.message('Failed to save run. Must be of the format <Ran 5.6 in h:m:s this is a comment> excluding the angle brackets.')
            return response
    else:
        if twilio_request.type is 'message':
            response.message(result)
            return response

    return response
