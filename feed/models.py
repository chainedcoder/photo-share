from django.conf import settings
from django.db import models

from photos.models import UploadedPhoto

FEED_TYPE = (
    (1, 'photo_liked'),
)


class Feed(models.Model):
    feed_type = models.IntegerField(choices=FEED_TYPE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_notification_to')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    latest_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='latest_user')
    description = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    # link to various stuff
    photo = models.ForeignKey(UploadedPhoto, null=True)

    class Meta:
        db_table = 'feed'
        default_permissions = ()
        ordering = ['-pk']

