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
        add_rep(interval_run, i)

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
    for i in range(100):
        dates.append(datetime.date.today() - datetime.timedelta(i))

    #set the type of workouts to generate
    types = [
        'Interval',
        'Normal',
        'Normal',
        'Interval',
        'CrossTrain',
        'Race',
        'Normal'
    ]
    #for each day, generate a workout
    for i in range(len(dates)):
        if types[i%7] == 'Interval':
            generate_interval_workout(athlete, dates[i])
        elif types[i%7] == 'Normal':
            generate_normal_workout(athlete, dates[i])
        elif types[i%7] == 'CrossTrain':
            generate_xtrain_workout(athlete, dates[i])


def create_athlete(season, info):
    #create user
    user = User.objects.create_user(info[0]+info[1], info[0]+info[1]+'@hamilton.edu', 'iam'+info[0])
    user.first_name = info[0]
    user.last_name = info[1]
    user.save()

    #create athlete
    athlete = Athlete.objects.create(
        user=user,
        graduation_year = info[2]
    )
    athlete.season = season,

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

def generate():
    team = Team.objects.create(
        school_name="Hamilton",
        gender = "M"
    )
    team.save()

    season = Season.objects.create(
        team = team,
        year = 2016,
        sport = "XC"
    )
    season.save()

    generate_athletes(season)

    #Generate four superusers, one for each of us.
    # I commented this out because it doesn't really make
    # sense for us to develop as anything other than a coach or
    # an athlete. I gave athletes the ability to be superusers though,
    # so that if you are logged in as an athlete you can access the admin page
    # names_passes = [
    #     ('jack', 'iamjack'),
    #     ('lexie', 'iamlexie'),
    #     ('mikey', 'iammikey'),
    #     ('emily', 'iamemily')
    # ]
    #
    # for name, password in names_passes:
    #     user = User.objects.create_user(name, name+'@hamilton.edu', 'iam'+name, is_staff=True, is_superuser=True)

def clean_database():
    Team.objects.all().delete()
    Season.objects.all().delete()
    Athlete.objects.all().delete()
    User.objects.all().delete()
