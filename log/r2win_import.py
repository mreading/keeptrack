import datetime
import re
import xml.etree.ElementTree as ET
from django.utils.encoding import smart_str, smart_unicode
from .models import *

# This is an interim class to ease the transition from the xml import file
# to django. That way, if the format of the xml files ever changes,
# the change to django won't be as complicated, it will just involve changing
# this object

class RaceInfo:
    def __init__(self, info):
        self.location = ""
        self.gender = "M"
        self.distance = ""
        self.units = ""
        self.duration =""
        self.place = ""

def process_cross_training(root):
    children = list(root)
    description = ""
    count = ""
    value = ""
    collector = []
    for el in children:
        if el.tag =="Description":
            collector.append([str(el.text)])
        elif el.tag == "Count":
            collector[-1].append(el.text)
        elif el.tag == "Value":
            collector[-1].append(el.text)

    retstr = "\nCross Training:\n"
    for lst in collector:
        for el in lst:
            if el != None:
                retstr += el + ", "
        retstr += "\n"
    return retstr

def process_set(xmlset):
    children = list(xmlset)
    for child in children:
        if child.tag == "Reps":
            num_reps = int(child.text)
        elif child.tag == "Distance":
            distance = int(child.text.split()[0])
            units = int(child.text.split()[0])

class Repeat:
    def __init__(self, stuff):
        print stuff.tag
        self.distance = str(stuff.find('Distance').text)
        self.count = str(stuff.find('Reps').text)
        self.goal = str(stuff.find('Goal').text)
        self.actual = str(stuff.find('Actual').text)
        self.rest = str(stuff.find('RepRest').text)
        print str(self)

    def __str__(self):
        return "{0} X {1} at {2} (goal {3}) with rest {4}".format(
            self.count, self.distance, self.actual, self.goal, self.rest
        )


class IntervalInfo:
    def __init__(self, info):
        self.warmup = 0
        self.cooldown = 0
        self.units = ""
        self.wu_units = ""
        self.cd_units = ""
        self.distance = ""
        self.repeats = []
        sets = list(info)
        for a in sets:
            if a.tag == "WarmUp":
                self.warmup = a.text
            elif a.tag == "CoolDown":
                self.cooldown = a.text
            elif a.tag == "Set":
                self.repeats.append(str(Repeat(a)))

    def __str__(self):
        retstr = "Interval Details:\n"
        for rep in self.repeats:
            retstr += rep + "\n"

        return retstr

class Workout:
    def __init__(self, xml_workout):
        attributes = list(xml_workout)
        self.date = datetime.datetime.today()
        self.time_of_day_description = ""
        self.run_type = ""
        self.total_distance = ""
        self.total_time = datetime.timedelta(0)
        self.running_miles = 0
        self.terrain = ""
        self.private_notes = ""
        self.shoe_name = ""
        self.comments = ""
        self.max_hr = ""
        self.avg_hr = ""
        self.difficulty = ""
        self.units = ""
        self.cross_training = ""
        self.sleep_hours = ""
        self.intervals = ""
        for a in attributes:
            if a.tag == "Date":
                self.date = datetime.datetime.strptime(a.text, "%A, %m/%d/%Y")
            elif a.tag == "TimeOfDayDescription":
                self.time_of_day_description = a.text
            elif a.tag == "RunTypeDescription":
                self.run_type = a.text
            elif a.tag == "TotalDistance":
                if a.text == "0":
                    self.total_distance = 0
                    self.units = "Miles"
                else:
                    self.total_distance, self.units = a.text.split()
                    self.total_distance = float(self.total_distance)
            elif a.tag == "TotalTime":
                time = a.text.split('[')[0]
                time = time.split(':')
                time = [int(t) for t in time]
                if len(time) == 3:
                    self.total_time = datetime.timedelta(hours=time[0], minutes=time[1], seconds=time[2])
                elif len(time) == 2:
                    self.total_time = datetime.timedelta(minutes=time[0], seconds=time[1])
                else:
                    self.total_time = datetime.timedelta(hours=0)
            elif a.tag == "RunningMiles":
                self.running_miles = a.text
            elif a.tag == "TerrainTypeDescription":
                self.terrain = a.text
            elif a.tag == "TotallyPrivateNotes":
                self.private_notes = a.text
            elif a.tag == "ShoeName":
                self.shoe_name += str(a.text)
            elif a.tag == "Comments":
                self.comments = smart_str(a.text)
            elif a.tag == "Intervals":
                self.intervals = str(IntervalInfo(a))
            elif a.tag == "MaxHeartRate":
                self.max_hr = int(a.text.split()[0])
            elif a.tag == "HeartRate":
                self.avg_hr = int(a.text.split()[0])
            elif a.tag == "Difficulty":
                self.difficulty = a.text
            elif a.tag == "RaceInformation":
                for attr in a.getchildren():
                    self.comments +=str(a.text)
            elif a.tag == "CrossTraining":
                self.cross_training = process_cross_training(a)
            elif a.tag == "HoursOfSleep":
                self.sleep_hours = a.text
            else:
                print "unrecognized tag {0}".format(a.tag)

    def __str__(self):
        return "{0} {1} in {2} ".format(
            self.total_distance,
            self.units,
            self.total_time
        )

def django_ify(workout, athlete):
    if workout.total_distance == 0:
        return
    run_type = ""
    if (workout.run_type == "Normal Run"
        or workout.run_type == "Easy Run"
        or workout.run_type == "Long Run"
        or workout.run_type == "wu/cd"
        or workout.run_type == "Speed Training"
        or workout.run_type == "Tempo"
        or workout.run_type == "Fartlek"):
        run_type = "NormalRun"
    elif workout.run_type == "Cross Training/Other":
        run_type = "CrossTrain"
    elif workout.run_type == "Interval Workout":
        run_type = "IntervalRun"
    elif workout.run_type == "Race":
        run_type = "Event"
    else:
        run_type = "NormalRun"

    activity = Activity.objects.create(
        athlete=athlete,
        date=workout.date,
        comment = workout.comments,
        act_type = run_type,
        user_label=workout.run_type,
        private_comments=workout.private_notes
    )
    if workout.cross_training != "":
        activity.comment = activity.comment + "\n" + workout.cross_training
    if workout.intervals != "":
        activity.comment = activity.comment + "\n" + workout.intervals
    activity.save()
    thread = Thread.objects.create(activity=activity)
    thread.save()

    if run_type == "NormalRun":
        run = NormalRun.objects.create(
            activity=activity,
            distance=workout.total_distance,
            units=workout.units,
            duration=workout.total_time,
            #shoe
            #surface
            #route
        )
        run.set_pace()
        run.save()

    elif run_type == "CrossTrain":
        run = CrossTrain.objects.create(
            activity=activity,
            distance=workout.total_distance,
            units=workout.units,
            duration=workout.total_time
        )
        run.save()

    elif run_type == "IntervalRun":
        run = IntervalRun.objects.create(
            activity=activity,
            warmup=0,
            cooldown=0,
            units="Miles",
            wu_units="Miles",
            cd_units="Miles",
            distance=workout.total_distance
        )
        run.save()

    elif run_type == "Event":
        meet = Meet.objects.create(
            location="test location"
        )
        meet.save()
        event = Event.objects.create(
            activity=activity,
            meet=meet,
            gender="M",
            distance=workout.total_distance,
            units=workout.units,
            duration=workout.total_time,
            place=0
        )
        event.set_pace()


def import_from_file(f, athlete):
    tree = ET.parse(f)
    root = tree.getroot()
    all_data = list(root)
    # first three elements are 'member', 'to' and 'from' dates of workouts,
    # so ignore them using a slice.
    workouts = all_data[3:]
    py_workouts = [Workout(w) for w in workouts]
    for w in py_workouts:
        django_ify(w, athlete)
