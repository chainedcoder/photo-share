from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone


class Follow(models.Model):
    FOLLOW_STATUS = (
        (0, 'Pending'),
        (1, 'Accepted'),
        (-1, 'Rejected')
    )
    user_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user')  # one who requested
    # one whom the request was sent to
    user_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower')
    status = models.IntegerField(choices=FOLLOW_STATUS, default=0)
    date_requested = models.DateTimeField(default=timezone.now)
    date_accepted = models.DateTimeField(null=True)

    class Meta:
        db_table = "follows"
        verbose_name = 'Follow'
        verbose_name_plural = "Follows"
        default_permissions = ()


class Block(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocker')
    blockee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blockee')
    date_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "blocks"
        verbose_name = 'Block'
        verbose_name_plural = "Blocks"
        default_permissions = ()
