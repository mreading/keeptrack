#------------------------------------------------------------------------------
# PURPOSE: generation of fake data for the developer testing purposes.
# USAGE: python manage.py shell -> from log.generate import * ->
#        clean_database()       -> generate()
# FILES: Pretty much standalone
#------------------------------------------------------------------------------
from models import *
from athlete_utils import *
import datetime
from random import uniform, randrange, choice
from django.contrib.auth.models import User

# To clear out database completely, do:
# > python manage.py flush

def generate_meet(athlete, date):
    event_distance = choice([5000, 8000, 3000, 10000])
    location = choice(['Rochester', 'Hamilton', 'Geneseo', 'Ithaca', 'Potsdam'])
    gender = 'M'
    units = 'Meters'

    seconds = int((event_distance/1000) * 200 * uniform(1.2, 0.8))
    duration = timedelta(seconds=seconds)

    activity = Activity.objects.create(
        athlete=athlete,
        date=date,
        comment="What a race!",
        act_type="Event"
    )
    activity.save()

    thread = Thread.objects.create(activity=activity)
    thread.save()

    meet = Meet.objects.create(
        location=location
    )
    meet.save()

    event = Event.objects.create(
        activity=activity,
        meet=meet,
        gender=gender,
        distance=event_distance,
        units=units,
        duration=duration,
        place=randrange(1, 300)
    )
    event.set_pace()
    event.save()

def add_rep(interval_run, position):
    #create a repeat object given an interval run object"
    rep = Rep.objects.create(
        interval_run = interval_run,
        distance = 800,
        units = "Meters",
        duration = timedelta(seconds=120+randrange(05, 45)),
        rest = timedelta(seconds=60),
        position = position
    )
    rep.save()

def generate_interval_workout(athlete, date):
    """ generate an interval workout for an athlete """
    activity = Activity.objects.create(
        athlete=athlete,
        date=date,
        comment="Here is a comment about how this interval workout went",
        act_type='IntervalRun'
    )
    activity.save()
    thread = Thread.objects.create(activity=activity)
    thread.save()

    units = ['Miles','Kilometers']

    interval_run = IntervalRun.objects.create(
        activity=activity,
        warmup=round(uniform(1.0, 2.5), 2),
        cooldown=round(uniform(1.0,2.5), 2),
        wu_units=choice(units),
        cd_units=choice(units),
    )

    interval_run.save()

    num_reps = randrange(3,10)
    for i in range(num_reps):
        add_rep(interval_run, i + 1)

    set_total_distance(interval_run)
    interval_run.save()

def generate_normal_workout(athlete, date):
    """ generate a normal workout for an athlete """
    activity = Activity.objects.create(
        athlete=athlete,
        date=date,
        comment="Here is a comment about this normal run.",
        act_type='NormalRun'
    )
    activity.save()
    thread = Thread.objects.create(activity=activity)
    thread.save()

    distance = round(uniform(3.5, 13.8), 2)
    minutes = distance * uniform(.7, 1.3) * 7

    normal_run = NormalRun.objects.create(
        activity=activity,
        distance=distance,
        units = choice(['Kilometers', 'Miles']),
        duration = timedelta(minutes=minutes)
    )
    normal_run.set_pace()
    normal_run.save()

def generate_xtrain_workout(athlete, date):
    """ generate a cross train workout for an athlete """
    activity = Activity.objects.create(
        athlete=athlete,
        date=date,
        comment="Here is a comment about this cross training activity",
        act_type='CrossTrain'
    )
    activity.save()
    thread = Thread.objects.create(activity=activity)
    thread.save()

    distance = round(uniform(3.5, 13.8), 2)
    minutes = distance * uniform(.7, 1.3) * 7

    xtrain = CrossTrain.objects.create(
        activity=activity,
        distance=distance,
        duration = timedelta(minutes=minutes),
        sport=choice(['Biking', 'Kayaking', 'Swimming', 'Skiing'])
    )
    xtrain.save()

def generate_workout_data(athlete):
    #get dates for last 7 days
    dates = []
    for i in range(300):
        dates.append(datetime.date.today() - datetime.timedelta(i))

    #set the type of workouts to generate
    types = [
        'Interval',
        'Normal',
        'Normal',
        'CrossTrain',
        'Race',
        'Normal',
        'Off'
    ]
    #for each day, generate a workout
    for i in range(len(dates)):
        if types[i%7] == 'Interval':
            generate_interval_workout(athlete, dates[i])
        elif types[i%7] == 'Normal':
            generate_normal_workout(athlete, dates[i])
        elif types[i%7] == 'CrossTrain':
            generate_xtrain_workout(athlete, dates[i])
        elif types[i%7] == 'Race':
            generate_meet(athlete, dates[i])


def create_athlete(season, info):
    #create user
    user = User.objects.create_user(info[0]+info[1], info[0]+info[1]+'@hamilton.edu', 'iam'+info[0], is_staff=True, is_superuser=True)
    user.first_name = info[0]
    user.last_name = info[1]
    user.save()

    #create athlete
    athlete = Athlete.objects.create(
        user=user,
        graduation_year = info[2],
        log_private = choice([True, False]),
    )
    athlete.seasons = season,

    #save user/athlete
    athlete.save()

    generate_workout_data(athlete)


def generate_athletes(season):
    seed_info = [
        ('Jack', 'Pierce', 2017),
        ('Grant', 'Whitney', 2017),
        ('Henry', 'Whipple', 2018),
        ('Peter', 'Deweirdt', 2018),
        ('Erich', 'Wohl', 2018),
        ('Andrew', 'Sinclair', 2018),
        ('Colin', 'Horgan', 2019),
        ('Reilly', 'Shew', 2019),
        ('Ben', 'Stoller', 2019),
        ('Bryce', 'Murdick', 2020),
        ('Jacob', 'Colangelo', 2020),
        ('Matthew', 'Reading', 2020),
        ('Christopher', 'Skeldon', 2020),
        ('Conor', 'Courtney', 2020),
        ('Francis', 'Zuroski', 2020),
        ('Andrew', 'Wheeler', 2020),
    ]

    for info in seed_info:
        create_athlete(season, info)

def generate_coaches(team):
    user = User.objects.create_user(
        "BrettHull",
        "BrettHull@hamilton.edu",
        "iamBrett",
        is_staff=True,
        is_superuser=True
    )
    user.save()
    coach = Coach.objects.create(user=user)
    coach.save()
    coach.teams.add(team)

def generate():
    team = Team.objects.create(
        school_name="Hamilton",
        gender = "M",
        sport = "XC",

    )
    team.save()

    season = Season.objects.create(
        year = 2016,
        start_date = datetime.date(year=2016, month=8, day=25),
        end_date = datetime.date(year=2016, month=11, day=20)
    )
    team.seasons.add(season)

    generate_coaches(team)
    generate_athletes(season)


def clean_database():
    Activity.objects.all().delete()
    Team.objects.all().delete()
    Season.objects.all().delete()
    Athlete.objects.all().delete()
    User.objects.all().delete()
