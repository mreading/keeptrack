from twilio import twiml
from django_twilio.decorators import twilio_view
# include decompose in your views.py
from django_twilio.request import decompose

@twilio_view
def inbound(request):
    print "moose"
    response = twiml.Response()

    # Create a new TwilioRequest object
    twilio_request = decompose(request)
    print twilio_request

    # See the Twilio attributes on the class
    print twilio_request.to
    print twilio_request.body
    print dir(twilio_request)
    # Discover the type of request
    if twilio_request.type is 'message':
        response.message('Thanks for the message!')
        return response

    # Handle different types of requests in a single view
    if twilio_request.type is 'voice':
        return voice_view(request)

    return response
