# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-15 15:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0017_auto_20161004_1832'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coach',
            old_name='team',
            new_name='teams',
        ),
    ]
