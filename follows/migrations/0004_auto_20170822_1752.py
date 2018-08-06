# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('follows', '0003_auto_20170810_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Accepted'), (2, 'Rejected'), (3, 'Cancelled'), (4, 'Friendship Cancelled')], default=0),
        ),
    ]
