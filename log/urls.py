from django.conf.urls import url
import django

from . import views
from . import athlete_views
from . import auth_views
from . import calendar_views
from . import race_views
from . import stats_views
from . import team_views
from . import workout_views

import os

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login_view, name='login'),
    url(r'^athlete/$', athlete_views.athlete, name='athlete'),
    url(r'^calendar/$', calendar_views.calendar, name='calendar'),
    url(r'^race_analysis/$', race_views.race_analysis, name='race_analysis'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^team_stats/$', stats_views.team_stats, name='team_stats'),
    url(r'^team/$', team_views.team, name='team'),
    url(r'^logout/$', auth_views.logout_view, name='logout'),
    url(r'^signup/$', auth_views.signup, name='signup'),
    url(r'^workout_templates/$', workout_views.workout_templates, name='workout_templates'),
]
