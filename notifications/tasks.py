from __future__ import absolute_import

from django.core.mail import send_mail

from celery import task
from celery.utils.log import get_task_logger
from django.core.cache import cache

from .models import Notification
from photoshare.settings import DEFAULT_FROM_EMAIL as sender_email


@task
def send_notifications():
    LOCK_EXPIRE = 60 * 5    # Lock expires in 5 minutes

    notifications = Notification.objects.filter(status=0)
    if notifications.count() > 0:
        for notification in notifications:
            # The cache key consists of the task name and the notification ID
            lock_id = '{0}-lock-{1}'.format("Send", notification.id)

            # cache.add fails if if the key already exists
            acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)

            # memcache delete is very slow, but we have to use it to take
            # advantage of using add() for atomic locking
            release_lock = lambda: cache.delete(lock_id)
            sender = sender_email
            if acquire_lock():
                try:
                    if notification.mode == 1:    # Send email notification
                        if notification.recipient:
                            recipients = [notification.recipient.email, ]
                        else:
                            recipients = [notification.email_address, ]
                        send_mail(
                            notification.subject, notification.content,
                            sender, recipients)
                        notification.status = 1
                        notification.save()
                    elif notification.mode == 2:
                        # push notification
                        pass
                finally:
                    release_lock()
