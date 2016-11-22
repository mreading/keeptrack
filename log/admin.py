from django.contrib import admin
from models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class AthleteInLine(admin.StackedInline):
    model = Athlete
    can_delete = False
    verbose_name_plural = 'Athlete'

class CoachInLine(admin.StackedInline):
    model = Coach
    can_delete = False
    verbose_name_plural = 'Coach'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (AthleteInLine, CoachInLine)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Team)
admin.site.register(Season)
admin.site.register(Athlete)
admin.site.register(Coach)
admin.site.register(Activity)
admin.site.register(Meet)
admin.site.register(Event)
admin.site.register(CrossTrain)
admin.site.register(NormalRun)
admin.site.register(IntervalRun)
admin.site.register(Rep)
admin.site.register(Thread)
admin.site.register(Comment)
admin.site.register(Bug)
admin.site.register(Announcement)
admin.site.register(Shoe)
