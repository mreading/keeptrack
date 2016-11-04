#------------------------------------------------------------------------------
# PURPOSE: Helper functions from athlete_views.py
# FILES: ./athlete_views.py
#------------------------------------------------------------------------------
from .utils import *
from .models import *
from .athlete_forms import *

def get_prs(athlete):
    activities = Activity.objects.filter(act_type='Event', athlete=athlete)
    events = [Event.objects.filter(activity=a)[0] for a in activities]
    prs = {}
    for e in events:
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
    # FIXME milliseconds are hardcoded
    return [hours, minutes, seconds, 0]

def get_interval_graph_data(reps):
    graph_data = [['Date', 'Miles', {'role':'style'}]]
    for rep in reps:
        # [place, [hour, minute, second, millisecond]]
        graph_data.append([rep.position, make_duration_chartable(rep.duration), 'color:#abcabc'])
    return graph_data

def get_workout_from_activity(activity):
    """---------------------------------------------------------
	  Given an activity, return the corrosponding run
	---------------------------------------------------------"""
    if activity.act_type == "NormalRun":
        return NormalRun.objects.get(activity=activity)
    if activity.act_type == "IntervalRun":
        return IntervalRun.objects.get(activity=activity)
    if activity.act_type == "CrossTrain":
        return CrossTrain.objects.get(activity=activity)
    if activity.act_type == "Event":
        return Event.objects.get(activity=activity)
    else:
        print "Unknown type of workout"

def build_graph_data(dates, activities, week_name_labels=False):
    """---------------------------------------------------------
	Build the data array for google charts mileage on the athlete
    page given a bunch of dates and activites.
    Dates are datetime objects.
	---------------------------------------------------------"""
    #change this to change the color of the bars in bar graphs for different types of runs.
    colors = {
        'NormalRun':'#6b7a8f',
        'IntervalRun':'#f7c331',
        'CrossTrain':'#dcc7aa',
        'Event':'#f7882f',
        'OffDay':'#111111' #immaterial, because days off have no color.
    }

    #graph data is expected to be of the form [[x-axis data, y-axis data], ...]
    # where x axis is a date string and y axis is floating point number representing distance
    graph_data = [['Date', 'Miles', {'role':'style'}, 'Link']]

    graph_data2 = [['Date', 'NormalRun', 'IntervalRun', 'CrossTrain', 'Event', {'role':'style'}, 'Link']]
    ##MAYBE PASS LEGEND HERE???
    #??????????????????????????????????????????????????????//
    #????
    #????????????????????????////
    validPoint=False

    p = 0
    i = 0
    while i < len(dates):
        if p < len(activities) and dates[i] == activities[p].date:
            validPoint = True
            w_date = activities[p].date
            distance = get_miles(get_workout_from_activity(activities[p]))

            #add distances of other runs
            if str(w_date) == graph_data[-1][0]:
                distance += graph_data[-1][1]

            if week_name_labels:
                w_date = w_date.strftime("%A")
            graph_data.append([
                str(w_date),
                distance,
                'color:'+colors[activities[p].act_type],
                '/log/athlete/activity_detail/'+str(activities[p].id),
            ])

            graph_data2.append([str(w_date), None, None, None, None, 'color:'+colors[activities[p].act_type],
                '/log/athlete/activity_detail/'+str(activities[p].id),])
            graph_data2[len(graph_data2)-1][graph_data2[0].index(activities[p].act_type)] = distance


            p += 1
            if p < len(activities) and dates[i] == activities[p].date:
                i = i
            else:
                i += 1
        else:
            w_date = dates[i]
            if week_name_labels:
                w_date = w_date.strftime("%A")
            graph_data.append(
            [str(w_date), None, 'color:'+colors['OffDay'], 'nothing']
            )

            graph_data2.append([str(w_date), None, None, 0, 0, 'color:'+colors['OffDay'],
                'nothing'])
            i += 1

    print graph_data
    print graph_data2
    if not validPoint:
        return False
    return graph_data2

def update_activity(activity, cleaned_data):
    run = None
    if activity.act_type == "NormalRun":
        run = NormalRun.objects.get(activity=activity)
    elif activity.act_type == "IntervalRun":
        run = IntervalRun.objects.get(activity=activity)
    elif activity.act_type == "CrossTrain":
        run = CrossTrail.objects.get(activity=activity)
    elif activity.act_type == "Event":
        run = Event.objects.get(activity=activity)


def get_post_form(run_type, post):
    """ Simply locates a form based on the type of run """
    if run_type == "NormalRun":
        return AddNormalForm(post)
    elif run_type == "IntervalRun":
        return AddIntervalForm(post)
    elif run_type == "CrossTrain":
        return AddXTrainForm(post)
    else:
        return AddEventForm(post)

def get_form(run_type):
    """ Very similar to the function above """
    if run_type == "NormalRun":
        return AddNormalForm()
    elif run_type == "IntervalRun":
        return AddIntervalForm()
    elif run_type == "CrossTrain":
        return AddXTrainForm()
    else:
        return AddEventForm()

def create_run(run_type, activity, data):
    """ ---------------------------------------------------------------
    Helper function for the athlete_views.add function to create a run
    -------------------------------------------------------------------"""
    if run_type == "NormalRun":
        run = NormalRun.objects.create(
            activity=activity,
            distance=round(float(data['distance']), 2),
            duration=data['duration'],
            units=data['units'],
        )
        run.set_pace()
    elif run_type == "IntervalRun":
        # Not implemented because it is handled in a seperate view
        pass
    elif run_type == "CrossTrain":
        run = CrossTrain.objects.create(
            activity=activity,
            distance=round(float(data['distance']), 2),
            duration=data['duration'],
            sport=data['sport'],
            units=data['units'],
        )
    elif run_type == "Event":
        # FIXME Need ability to locoate existing meet.
        meet = Meet.objects.create(
            location=data['location'],
        )
        meet.save()
        run = Event.objects.create(
            activity=activity,
            meet=meet,
            distance=round(float(data['distance']), 2),
            duration=data['duration'],
            place=data['place'],
            units=data['units'],
            gender=data['gender']
        )
        run.set_pace()
    run.save()

def set_total_distance(interval_run):
    """---------------------------------------------------------
    used to set the total distance attribute of inerval runs.
	---------------------------------------------------------"""
    reps = Rep.objects.filter(interval_run=interval_run)
    total = 0
    for r in reps:
        total += get_miles(r)

    #Calculate warm up distance
    if interval_run.wu_units == 'Miles':
        total += float(interval_run.warmup)
    elif interval_run.wu_units == 'Kilometers':
        total += kilometers_to_miles(interval_run.warmup)
    elif interval_run.wu_units == 'Meters':
        total += meters_to_miles(interval_run.warmup)

    #Calculate cool down distance
    if interval_run.cd_units == 'Miles':
        total += float(interval_run.cooldown)
    elif interval_run.cd_units == 'Kilometers':
        total += kilometers_to_miles(interval_run.cooldown)
    elif interval_run.cd_units == 'Meters':
        total += meters_to_miles(interval_run.cooldown)

    interval_run.distance = total
    interval_run.save()
