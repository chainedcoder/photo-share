# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedphoto',
            name='process_status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Completed')]),
        ),
    ]
