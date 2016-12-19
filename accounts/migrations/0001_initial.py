# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='email address')),
                ('username', models.CharField(unique=True, max_length=20, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, null=True, verbose_name='last name')),
                ('phone_number', models.CharField(max_length=30, null=True, verbose_name='phone number', validators=[django.core.validators.RegexValidator(regex='^[0-9]{9,15}$', message='Enter a valid phone number (9 - 15 digits).')])),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('email_verification_key', models.CharField(max_length=40, null=True, blank=True)),
                ('email_verification_key_expires', models.DateTimeField(null=True, blank=True)),
                ('phone_verification_code', models.IntegerField(null=True, blank=True)),
                ('phone_verification_code_expires', models.DateTimeField(null=True, blank=True)),
                ('account_verified_date', models.DateTimeField(null=True, blank=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_seen', models.DateTimeField(null=True, verbose_name='last seen', blank=True)),
                ('profile_pic', models.ImageField(null=True, upload_to='uploads/profile_pics')),
                ('tink_qrcode', models.ImageField(null=True, upload_to='tink_qrcodes')),
                ('bio', models.TextField(null=True, blank=True)),
                ('birthday', models.DateField(null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['id'],
                'default_permissions': (),
                'db_table': 'users',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='ProfileVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video_file', models.FileField(upload_to='user_videos')),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Processed')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
                'db_table': 'user_videos',
            },
        ),
    ]
