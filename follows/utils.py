from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import Follow


def are_friends(user_1, user_2):
    try:
        Follow.objects.get(
            Q(status=1), Q(user_1=user_1, user_2=user_2) | Q(user_2=user_1, user_1=user_2))
        return True
    except ObjectDoesNotExist:
        return False
