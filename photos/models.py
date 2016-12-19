from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings

BASE_UPLOAD_PATH = 'uploads/user_photos'

IMAGE_PROCESS_STATUS = (
    (0, 'Pending'),
    (1, 'Completed')
)


class UploadedPhoto(models.Model):
    image = models.ImageField(upload_to=BASE_UPLOAD_PATH)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    location_latitude = models.FloatField(null=True)
    location_longitude = models.FloatField(null=True)
    city_name = models.CharField(max_length=150, null=True)
    country_name = models.CharField(max_length=150, null=True)
    time_uploaded = models.DateTimeField(default=timezone.now)
    faces_found = models.IntegerField(default=0)
    process_status = models.IntegerField(choices=IMAGE_PROCESS_STATUS, default=0)

    class Meta:
        db_table = 'uploaded_photos'
        verbose_name = "Uploaded Photo"
        verbose_name_plural = "Uploaded Photos"
        default_permissions = ()

    def __unicode__(self):
        pass


class PhotoStream(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='photos_from_user')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='photos_to_user')
    date_time = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)

    class Meta:
        db_table = 'photo_streams'
        verbose_name = "Photo Stream"
        verbose_name_plural = "Photo Streams"
        default_permissions = ()


class PhotoStreamPhoto(models.Model):
    stream = models.ForeignKey(PhotoStream)
    photo = models.ForeignKey(UploadedPhoto)
    liked = models.BooleanField(default=False)

    class Meta:
        db_table = 'photo_stream_photos'
        verbose_name = "Photo Stream Photo"
        verbose_name_plural = "Photo Stream Photos"
        default_permissions = ()

