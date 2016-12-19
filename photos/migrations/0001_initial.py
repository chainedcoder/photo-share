# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoStream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('seen', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(related_name='photos_from_user', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='photos_to_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'photo_streams',
                'verbose_name': 'Photo Stream',
                'verbose_name_plural': 'Photo Streams',
            },
        ),
        migrations.CreateModel(
            name='PhotoStreamPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('liked', models.BooleanField(default=False)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'photo_stream_photos',
                'verbose_name': 'Photo Stream Photo',
                'verbose_name_plural': 'Photo Stream Photos',
            },
        ),
        migrations.CreateModel(
            name='UploadedPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to='uploads/user_photos')),
                ('location_latitude', models.FloatField(null=True)),
                ('location_longitude', models.FloatField(null=True)),
                ('city_name', models.CharField(max_length=150, null=True)),
                ('country_name', models.CharField(max_length=150, null=True)),
                ('time_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('faces_found', models.IntegerField(default=0)),
                ('process_status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Completed')])),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'uploaded_photos',
                'verbose_name': 'Uploaded Photo',
                'verbose_name_plural': 'Uploaded Photos',
            },
        ),
        migrations.AddField(
            model_name='photostreamphoto',
            name='photo',
            field=models.ForeignKey(to='photos.UploadedPhoto'),
        ),
        migrations.AddField(
            model_name='photostreamphoto',
            name='stream',
            field=models.ForeignKey(to='photos.PhotoStream'),
        ),
    ]
