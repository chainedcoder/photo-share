# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 09:19
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0006_auto_20170801_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photostream',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='uploadedphoto',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
