from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import Follow


def are_friends(user_1, user_2):
    try:
        Follow.objects.get(
            Q(status=1), Q(user_from=user_1, user_to=user_2) | Q(user_from=user_2, user_to=user_1))
        return True
    except ObjectDoesNotExist:
        return False


def friend_request_exists(user_1, user_2):
    try:
        Follow.objects.get(
            Q(status=0), Q(user_from=user_1, user_to=user_2) | Q(user_from=user_2, user_to=user_1))
        return True
    except ObjectDoesNotExist:
        return False
