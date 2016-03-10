# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 10:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photos', '0002_auto_20160305_0144'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoStream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'photo_streams',
                'verbose_name': 'Photo Stream',
                'verbose_name_plural': 'Photo Streams',
            },
        ),
        migrations.CreateModel(
            name='PhotoStreamUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photos.PhotoStream')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'photo_stream_users',
                'verbose_name': 'Photo Stream User',
                'verbose_name_plural': 'Photo Stream Users',
            },
        ),
        migrations.AlterModelOptions(
            name='uploadedphoto',
            options={'default_permissions': (), 'verbose_name': 'UploadedPhoto', 'verbose_name_plural': 'UploadedPhotos'},
        ),
        migrations.AddField(
            model_name='photostream',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photos.UploadedPhoto'),
        ),
    ]