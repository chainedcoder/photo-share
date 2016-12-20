# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_auto_20161219_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photostreamphoto',
            name='stream',
            field=models.ForeignKey(related_name='images', to='photos.PhotoStream'),
        ),
    ]
