from log.models import *

def migrate_data():
    norms = NormalRun.objects.all()
    for n in norms:
        n.activity.distance = n.distance
        n.activity.duration = n.duration
        n.activity.units = n.units
        n.activity.pace = n.pace
        n.activity.save()

    xtrains = CrossTrain.objects.all()
    for x in xtrains:
        x.activity.distance = x.distance
        x.activity.units = x.units
        x.activity.duration = x.duration
        x.activity.sport = x.sport
        x.activity.save()

    iruns = IntervalRun.objects.all()
    for i in iruns:
        i.activity.warmup = i.warmup
        i.activity.cooldown = i.cooldown
        i.activity.wu_units = i.wu_units
        i.activity.cd_units = i.cd_units
        i.activity.distance = i.distance
        i.activity.save()
        reps = Rep.objects.filter(interval_run=i)
        for r in reps:
            r.activity = r.interval_run.activity
            r.save()

    events = Event.objects.all()
    for e in events:
        e.activity.meet = e.meet
        e.activity.gender = e.gender
        e.activity.distance = e.distance
        e.activity.units = e.units
        e.activity.duration = e.duration
        e.activity.place = e.place
        e.activity.pace = e.pace
        e.activity.save()
