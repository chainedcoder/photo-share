# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0004_auto_20170316_1834'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photostreamphoto',
            options={'ordering': ['-pk'], 'default_permissions': (), 'verbose_name': 'Photo Stream Photo', 'verbose_name_plural': 'Photo Stream Photos'},
        ),
    ]
