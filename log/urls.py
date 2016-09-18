from django.conf.urls import url
import django

from . import views
import os

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^athlete/$', views.athlete, name='athlete'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^race_analysis/$', views.race_analysis, name='race_analysis'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^team_stats/$', views.team_stats, name='team_stats'),
    url(r'^team/$', views.team, name='team'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^workout_templates/$', views.workout_templates, name='workout_templates'),
]
