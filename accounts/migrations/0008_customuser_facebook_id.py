# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160311_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='facebook_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
