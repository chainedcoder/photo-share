import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q


class Follow(models.Model):
    FOLLOW_STATUS = (
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Rejected'),
        (3, 'Cancelled'),
        (4, 'Friendship Cancelled')
    )
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user_from')  # one who requested
    user_from_to_user_to = models.BooleanField(default=True)

    # one whom the request was sent to
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user_to')
    user_to_to_user_from = models.BooleanField(default=True)

    status = models.IntegerField(choices=FOLLOW_STATUS, default=0)
    date_requested = models.DateTimeField(auto_now_add=True)
    date_accepted = models.DateTimeField(null=True)

    public_id = models.UUIDField(default=uuid.uuid4)

    class Meta:
        db_table = "follows"
        verbose_name = 'Follow'
        verbose_name_plural = "Follows"
        default_permissions = ()

    @staticmethod
    def check_auto_send(from_user_id, to_user_id):
        from_user_id = int(from_user_id)
        to_user_id = int(to_user_id)
        try:
            friendship = Follow.objects.get(Q(user_from_id=from_user_id, user_to_id=to_user_id) | Q(user_from_id=to_user_id, user_to_id=from_user_id), status=1)
            if friendship.user_from_id == from_user_id and friendship.user_to_id == to_user_id:
                return friendship.user_from_to_user_to
            elif friendship.user_from_id == to_user_id and friendship.user_to_id == from_user_id:
                return friendship.user_to_to_user_from
        except ObjectDoesNotExist:
            return True
