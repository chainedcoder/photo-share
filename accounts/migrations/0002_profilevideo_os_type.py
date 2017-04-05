# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilevideo',
            name='os_type',
            field=models.PositiveIntegerField(null=True, choices=[(1, 'Android'), (2, 'iOS')]),
        ),
    ]
