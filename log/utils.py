from django.core.mail import send_mail

def send_announcement(announcement, season):
    athletes = list(season.athlete_set.all())
    emails = [a.user.email for a in athletes]
    send_mail(
        'New Announcement',             # Subject
        announcement,                   # Message
        'keeptrack.hamilton@gmail.com', # From
        emails,                         # To
        fail_silently=False,
    )

#This is the file where commonly used functions go
def miles_to_kilometers(miles):
    return miles * 1.609344

def kilometers_to_miles(kilometers):
    return kilometers * 0.621371

def meters_to_kilometers(meters):
    return meters/1000.0

def kilometers_to_meters(kilometers):
    return kilometers * 1000

def meters_to_miles(meters):
    return kilometers_to_miles(meters_to_kilometers(meters))

def miles_to_meters(miles):
    return kilometers_to_meters(miles_to_kilometers(miles))

def get_miles(obj):
    if obj.units == 'Miles':
        return obj.distance
    elif obj.units == 'Meters':
        return  meters_to_miles(obj.distance)
    elif obj.units == 'Kilometers':
        return  kilometers_to_miles(obj.distance)
    else:
        print "ERROR IN GET_MILES"

def get_kilometers(obj):
    if obj.units == 'Miles':
        return miles_to_kilometers(obj.distance)
    elif obj.units == 'Meters':
        return meters_to_kilometers(obj.distance)
    elif obj.units == 'Kilometers':
        return obj.distance
    else:
        print "ERROR IN GET_KILOMETERS"

def get_meters(obj):
    if obj.units == 'Miles':
        return miles_to_meters(obj.distance)
    elif obj.units == 'Meters':
        return obj.distance
    elif obj.units == 'Kilometers':
        return kilometers_to_meters(obj.distance)
    else:
        print "ERROR IN GET_MILES"
