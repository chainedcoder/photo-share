# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 09:10
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0005_auto_20170317_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='photostream',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='uploadedphoto',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
