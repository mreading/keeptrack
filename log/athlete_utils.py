from .utils import *
from .models import *
from .athlete_forms import *
def get_post_form(run_type, request):
    if run_type == "NormalRun":
        return AddNormalForm(request)
    elif run_type == "IntervalRun":
        return AddIntervalForm(request)
    elif run_type == "CrossTrain":
        return AddXtrainForm(request)
    else:
        return AddEventForm(request)

def get_form(run_type):
    if run_type == "NormalRun":
        return AddNormalForm()
    elif run_type == "IntervalRun":
        return AddIntervalForm()
    elif run_type == "CrossTrain":
        return AddXtrainForm()
    else:
        return AddEventForm()

def create_run(run_type, activity, data):
    if run_type == "NormalRun":
        run = NormalRun.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration'],
            units=data['units'],
        )
    elif run_type == "IntervalRun":
        pass
    elif run_type == "CrossTrain":
        run = CrossTrain.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration'],
            sport=data['sport'],
            units=data['units'],
        )
    else:
        run = Event.objects.create(
            activity=activity,
            distance=data['distance'],
            duration=data['duration'],
            location=data['location'],
            place=data['place'],
            units=data['units'],
        )
    run.save()

def set_total_distance(interval_run):
    #used to set the total distance attribute of inerval runs.
    reps = Rep.objects.filter(interval_run=interval_run)
    total = 0
    for r in reps:
        total += get_miles(r)

    #Calculate warm up distance
    if interval_run.wu_units == 'Miles':
        total += interval_run.warmup
    elif interval_run.wu_units == 'Kilometers':
        total += kilometers_to_miles(interval_run.warmup)
    elif interval_run.wu_units == 'Meters':
        total += meters_to_miles(interval_run.warmup)

    #Calculate cool down distance
    if interval_run.cd_units == 'Miles':
        total += interval_run.cooldown
    elif interval_run.cd_units == 'Kilometers':
        total += kilometers_to_miles(interval_run.cooldown)
    elif interval_run.cd_units == 'Meters':
        total += meters_to_miles(interval_run.cooldown)

    interval_run.total_distance = total
    interval_run.save()
