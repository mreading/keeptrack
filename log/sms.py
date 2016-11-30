from twilio import twiml
from django_twilio.decorators import twilio_view
# include decompose in your views.py
from django_twilio.request import decompose

@twilio_view
def inbound(request):

    response = twiml.Response()

    # Create a new TwilioRequest object
    twilio_request = decompose(request)

    # See the Twilio attributes on the class
    twilio_request.to
    # >>> '+44123456789'

    # Discover the type of request
    if twilio_request.type is 'message':
        response.message('Thanks for the message!')
        return response

    # Handle different types of requests in a single view
    if twilio_request.type is 'voice':
        return voice_view(request)

    return response
