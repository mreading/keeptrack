import datetime
import timeit
import re
import xml.etree.ElementTree as ET

from .models import *

class Workout:
    def __init__(self, xml_workout):
        attributes = list(xml_workout)
        self.date = ""
        self.time_of_day_description = ""
        self.run_type = ""
        self.total_distance = ""
        self.total_time = ""
        self.running_miles = ""
        self.terrain = ""
        self.private_notes = ""
        self.shoe_name = ""
        self.comments = ""
        self.max_hr = ""
        self.avg_hr = ""
        self.difficulty = ""
        self.units = ""
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
                self.shoe_name = a.text
            elif a.tag == "Comments":
                self.comments = a.text
            elif a.tag == "Intervals":
                print "here are some intervals"
            elif a.tag == "MaxHeartRate":
                self.max_hr = int(a.text.split()[0])
            elif a.tag == "HeartRate":
                self.avg_hr = int(a.text.split()[0])
            elif a.tag == "Difficulty":
                self.difficulty = a.text
            else:
                print "unrecognized tag {0}".format(a.tag)

    def __str__(self):
        return "{0} {1} in {2} ".format(
            self.total_distance,
            self.units,
            self.total_time
        )

def django_ify(workout, athlete):
    run_type = ""
    if (workout.run_type == "Normal Run"
        or workout.run_type == "Easy Run"
        or workout.run_type == "Long Run"):
        run_type = "NormalRun"
    elif workout.run_type == "Cross Training/Other":
        run_type = "CrossTrain"
    elif workout.run_type == "Interval Workout":
        run_type = "IntervalRun"
    elif workout.run_type == "Race":
        run_type = "Event"

    activity = Activity.objects.create(
        athlete=athlete,
        date=workout.date,
        comment = workout.comments,
        act_type = run_type
    )
    activity.save()

    thread = Thread.objects.create(activity=activity)
    thread.save()

    if run_type == "NormalRun":
        NormalRun.objects.create(
            activity=activity,
            distance=workout.total_distance,
            units=workout.units,
            duration=workout.total_time,
            #shoe
            #surface
            #route
        )
    elif run_type == "CrossTrain":
        CrossTrain.objects.create(
            activity=activity,
            distance=workout.total_distance,
            units=workout.units,
            duration=workout.total_time
        )
    elif run_type == "IntervalRun":
        # IntervalRun.objects.create(
        #
        # )
        activity.delete()
    elif run_type == "Race":
        activity.delete()


def import_from_file(f, athlete):
    tree = ET.parse(f)
    root = tree.getroot()
    all_data = list(root)
    #first three elements are 'member', 'to' and 'from' dates of workouts
    workouts = all_data[3:]
    py_workouts = [Workout(w) for w in workouts]
    print py_workouts
    for w in py_workouts:
        django_ify(w, athlete)
