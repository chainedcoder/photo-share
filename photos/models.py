from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone

BASE_UPLOAD_PATH = 'user_photos'


class UploadedPhoto(models.Model):
    image = models.ImageField(upload_to=BASE_UPLOAD_PATH)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    time_uploaded = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'uploaded_photos'
        verbose_name = "UploadedPhoto"
        verbose_name_plural = "UploadedPhotos"

    def __unicode__(self):
        pass
