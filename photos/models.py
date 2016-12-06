from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings

BASE_UPLOAD_PATH = 'uploads/user_photos'


class UploadedPhoto(models.Model):
    image = models.ImageField(upload_to=BASE_UPLOAD_PATH)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    time_uploaded = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'uploaded_photos'
        verbose_name = "Uploaded Photo"
        verbose_name_plural = "Uploaded Photos"
        default_permissions = ()

    def __unicode__(self):
        pass


class PhotoStream(models.Model):
    image = models.ForeignKey(UploadedPhoto)
    date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'photo_streams'
        verbose_name = "Photo Stream"
        verbose_name_plural = "Photo Streams"
        default_permissions = ()


class PhotoStreamUser(models.Model):
    stream = models.ForeignKey(PhotoStream)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = 'photo_stream_users'
        verbose_name = "Photo Stream User"
        verbose_name_plural = "Photo Stream Users"
        default_permissions = ()
