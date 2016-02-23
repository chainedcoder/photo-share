import hashlib
import datetime
import random

from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils import timezone

from rest_framework import serializers

from notifications.models import Notification
from notifications.tasks import send_notifications

from .models import Follow


class FollowRequestSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        source='user_1.username', read_only=True)
    name = serializers.CharField(
        source='user_1.get_full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'username', 'name')


class FriendSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        source='user.username', read_only=True)
    name = serializers.CharField(
        source='user.get_full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ('username', 'name')
