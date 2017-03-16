# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_auto_20161220_1322'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photostream',
            options={'ordering': ['-pk'], 'default_permissions': (), 'verbose_name': 'Photo Stream', 'verbose_name_plural': 'Photo Streams'},
        ),
    ]
