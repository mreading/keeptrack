from twilio import twiml
from django_twilio.decorators import twilio_view
# include decompose in your views.py
from django_twilio.request import decompose
from log.models import *
import re
import datetime

def process_sms_text(text, from_num):

    # extract the distance and time data
    exp = r'^(r|R)an (?P<distance>[0-9]+(\.[0-9]+)?)\s*in ((?P<hours>[0-9]*):)?(?P<minutes>[0-9]+):(?P<seconds>[0-9]+) (?P<comments>.*)'
    match = re.search(exp, text)
    if not match:
        return None
    distance = match.group('distance')
    hours = match.group('hours')
    if hours == None:
        hours = 0
    minutes = match.group('minutes')
    seconds = match.group('seconds')
    comments = match.group('comments')

    # find the athlete associated with that phobe number
    if from_num[0] == '+':
        from_num = from_num[1:]
    athlete = Athlete.objects.filter(phone_number=from_num)[0]
    activity = Activity.objects.create(
        athlete=athlete,
        date=datetime.date.today(),
        comment=comments
    )
    activity.save()

    run = NormalRun.objects.create(
        activity=activity,
        distance=float(distance),
        duration=datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))

    )
    run.set_pace()
    run.save()
    return "Your run has been saved!"


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
