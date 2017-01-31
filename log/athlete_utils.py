#------------------------------------------------------------------------------
# PURPOSE: Helper functions from athlete_views.py
# FILES: ./athlete_views.py
#------------------------------------------------------------------------------
from .utils import *
from .models import *
from .athlete_forms import *

from forecastiopy import *
from geopy.geocoders import Nominatim
import time

def wear_help(location):

    geolocator = Nominatim()
    location = geolocator.geocode(location)
    if location == None:
        return None
    lat = location.latitude
    lon = location.longitude

    fio = ForecastIO.ForecastIO("31d0c8f0c1036505d4f8541000fcc555", latitude=lat, longitude=lon)
    current = FIOCurrently.FIOCurrently(fio)

    tights_CO = 45
    temp = current.temperature
    #------------------------tights-----------------------------
    #adjust for wind
    if current.windSpeed > 5 and current.windSpeed < 10:
        tights_CO -= 5
    elif current.windSpeed > 10:
        tights_CO -= 10

    #calculate tights
    if temp > tights_CO:
        tights = "No tights today."
    else:
        tights = "Wear tights."

    #----------------------tops--------------------------------
    tops = ""
    adj_temp = temp - current.windSpeed

    if .85 < current.precipProbability <= 1 and current.icon == "rain":
        if adj_temp > 48:
            tops = "it will probably rain, but it is too warm to matter."
        else:
            tops = "It will probably rain, and it's pretty cold. Throw a windbreaker on top."

    if adj_temp > 60:
        tops += "Don't wear any shirt. It's time to get ur tan on."
    elif adj_temp > 48:
        tops += "A T-shirt will probably do it"
    elif adj_temp > 40:
        tops += "A long sleeve will work just fine."
    elif adj_temp > 34:
        tops += "It's a two shirt kind of day."
    elif adj_temp > 24:
        tops += "T-shirt, long sleeve, jacket."
    else:
        tops += "Wear at least two layers on top, one of which should be substantial. "

    #------------------------hat/glasses--------------------------
    if adj_temp < 30:
        hat = "Wear a winter hat."
    else:
        hat = "It's pretty cloudy. No need for a baseball hat or sunglasses."
        if current.cloudCover < .3:
            if current.windSpeed > 10:
                hat = "A hat might blow off today, but sunglasses are a good idea"
            else:
                hat = "Hats and sunglasses should be worn today"

    if current.icon == "snow":
        tops += " It is snowing, so glasses and gloves are the move"

    #-----------------------storm warning------------------------
    storm = "Unavailable"
    if "nearestStormDistance" in current.get().keys():
        storm = "Just so you know, the nearest storm is {0} miles away".format(current.nearestStormDistance)

    return {
        'location': location,
        'tights': tights,
        'tops': tops,
        'hat': hat,
        'storm': storm
    }

def get_prs(athlete):
    activities = Activity.objects.filter(act_type='Event', athlete=athlete)
    prs = {}
    for e in activities:
        if str(e.distance) in prs:
            if e.duration < prs[str(e.distance)].duration:
                prs[str(e.distance)] = e
        else:
            prs[str(e.distance)] = e
    return prs

def make_duration_chartable(duration):
    """-------------------------------------------------------
    Given a duration object, turn it into a list of the format
    [hours, minutes, seconds, milliseconds]
    -------------------------------------------------------"""
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    milliseconds = duration.microseconds / 1000
    return [hours, minutes, seconds, milliseconds]

def get_interval_graph_data(reps):
    graph_data = [['Date', 'Miles', {'role':'style'}]]
    for rep in reps:
        # [place, [hour, minute, second, millisecond]]
        graph_data.append([rep.position, make_duration_chartable(rep.duration), 'color:#f7c331'])
    return graph_data


def get_label(d, num_dates):
    if num_dates < 10:
        return d.strftime('%a %b %d')
    if num_dates < 15:
        return d.strftime('%a %d')
    if num_dates < 370:
        return d.strftime('%b %d')
    return str(d)

def build_graph_data(dates, athlete):
    total = 0
    colors = {
        'NormalRun':'#6b7a8f',
        'IntervalRun':'#f7c331',
        'CrossTrain':'#dcc7aa',
        'Event':'#dcc7aa',
        'OffDay':'#111111' #immaterial, because days off have no color.
    }
    indexes = {
        'NormalRun':1,
        'IntervalRun':2,
        'CrossTrain':3,
        'Event':4,
    }

    data = [['Date', 'Normal Run', 'Interval Run', 'Cross Train', 'Race', {'role':'style'}, 'Link']]
    date_iterator = 0
    athlete_acts = Activity.objects.filter(athlete=athlete)
    for d in dates:
        activities = athlete_acts.filter(
            date=d,
            act_type__in=['NormalRun', 'Event', 'IntervalRun', 'CrossTrain']
        )
        prep = [get_label(d,len(dates)), 0, 0, 0, 0,'color:'+colors['OffDay'], 'nolink']
        for a in activities:
            # Don't include cross training miles
            if a.act_type != 'CrossTrain':
                miles = get_miles(a)
            else:
                miles = 0
            prep[indexes[a.act_type]] += miles
            total += miles
            prep[-1] = "/log/athlete/activity_detail/"+str(a.id)+"/"
        data.append(prep)
    return data, round(total, 2)


def set_total_distance(activity):
    """---------------------------------------------------------
    used to set the total distance attribute of inerval runs.
	---------------------------------------------------------"""
    reps = Rep.objects.filter(activity=activity)
    total = 0
    for r in reps:
        total += get_miles(r, rep=True)

    #Calculate warm up distance
    if activity.wu_units == 'Miles':
        total += float(activity.warmup)
    elif activity.wu_units == 'Kilometers':
        total += kilometers_to_miles(activity.warmup)
    elif activity.wu_units == 'Meters':
        total += meters_to_miles(activity.warmup)

    #Calculate cool down distance
    if activity.cd_units == 'Miles':
        total += float(activity.cooldown)
    elif activity.cd_units == 'Kilometers':
        total += kilometers_to_miles(activity.cooldown)
    elif activity.cd_units == 'Meters':
        total += meters_to_miles(activity.cooldown)

    activity.distance = round(total, 2)
    activity.save()
