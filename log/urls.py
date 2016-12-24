from django.conf.urls import url, include
from . import views
from . import athlete_views
from . import auth_views
from . import calendar_views
from . import meet_views
from . import stats_views
from . import team_views
from . import workout_views
from . import coach_views
from . import sms

from axes.decorators import watch_login

import os

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^help/$', views.help, name='help'),
    url(r'^login/$', watch_login(auth_views.login_view), name='login'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^gear/', athlete_views.gear, name='gear'),
    url(r'^ajax/range_select/$', athlete_views.range_select, name='range_select'),
    url(r'^athlete/(?P<user_id>[0-9]+)/$', athlete_views.athlete, name='athlete'),
    url(r'^athlete/settings/(?P<user_id>[0-9]+)/$', athlete_views.settings, name='settings'),
    url(r'^coach/settings/(?P<user_id>[0-9]+)/$', coach_views.settings, name='coach_settings'),
    url(r'^calendar/$', calendar_views.calendar, name='calendar'),
    url(r'^event_analysis/$', meet_views.event_analysis, name='event_analysis'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^team_stats/$', stats_views.team_stats, name='team_stats'),
    url(r'^team/$', team_views.team, name='team'),
    url(r'^logout/$', auth_views.logout_view, name='logout'),
    url(r'^signup/$', auth_views.signup, name='signup'),
    url(r'^change_password/(?P<user_id>[0-9]+)/$', auth_views.change_password, name='change_password'),
    url(r'^workout_templates/$', workout_views.workout_templates, name='workout_templates'),
    url(r'^athlete/add/$', athlete_views.add, name='add'),
    url(r'^athlete/edit_activity/(?P<activity_id>[0-9]+)/$', athlete_views.edit_activity, name='edit_activity'),
    url(r'^athlete/activity_detail/(?P<activity_id>[0-9]+)/$', athlete_views.activity_detail, name='activity_detail'),
    url(r'^athlete/delete_activity/(?P<activity_id>[0-9]+)/$', athlete_views.delete_activity, name='delete_activity'),
    url(r'^athlete/r2w_import/$', athlete_views.r2w_import, name='r2w_import'),
    url(r'^create_season/(?P<user_id>[0-9]+)/(?P<team_id>[0-9]+)$', coach_views.create_season, name='create_season'),
    url(r'^manage_teams/(?P<user_id>[0-9]+)/$', coach_views.manage_teams, name='manage_teams'),
    url(r'^all_seasons/(?P<user_id>[0-9]+)/(?P<team_id>[0-9]+)/$', coach_views.all_seasons, name='all_seasons'),
    url(r'^add_team/(?P<user_id>[0-9]+)/$', coach_views.add_team, name='add_team'),
    url(r'^add_new_athletes/(?P<user_id>[0-9]+)/(?P<team_id>[0-9]+)/(?P<season_id>[0-9]+)/$', coach_views.add_athletes, name='add_athletes'),
    url(r'^add_athletes/(?P<user_id>[0-9]+)/(?P<team_id>[0-9]+)/(?P<season_id>[0-9]+)/$', coach_views.add_existing_athletes, name='add_existing_athletes'),
    url(r'^add_coach/(?P<user_id>[0-9]+)/$', coach_views.add_coach, name='add_coach'),
    url(r'^calendar/select_time_period/$', calendar_views.time_period, name='time_period'),
    url(r'^calendar/select_team_season/$', calendar_views.team_season, name='team_season'),
    url(r'^submit_bug/$', views.submit_bug, name='submit_bug'),
    url(r'^delete_bug/(?P<bug_id>[0-9]+)/$', views.delete_bug, name='delete_bug'),
    url(r'^wear/$', athlete_views.wear, name="wear"),
    url(r'^create_announcement/$', team_views.create_announcement, name='create_announcement'),
    url(r'^receive/$', sms.inbound, name="respond"),
    url(r'^report/$', sms.generate_report, name="report_test"),
 ]
