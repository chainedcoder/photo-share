from .models import Notification


def create_notification(recipient, subject, content):
    for i in range(1, 3):
        notification = Notification(mode=i)
        notification.recipient = recipient
        notification.subject = subject
        notification.content = content
        notification.save()
