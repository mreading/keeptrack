from django.conf.urls import url
import django

from . import views
import os

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login')

]
