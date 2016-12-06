from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings

"""
Notification Types and their values:
1 - Email alerts
2 - App Notifications
3 - Push Notifications
"""


class Notification(models.Model):
    MODES = (
        (1, 'Email'),
        (2, 'Push'),
    )
    STATUS = (
        (0, 'Pending'),
        (1, 'Successful'),
    )
    mode = models.IntegerField(choices=MODES)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True)
    content = models.TextField()
    subject = models.CharField(max_length=50, null=True)
    email_address = models.EmailField(null=True)
    phone_number = models.CharField(max_length=13, null=True)
    status = models.IntegerField(default=0, choices=STATUS)
    timestamp = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.subject

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        default_permissions = ()
