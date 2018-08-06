from rest_framework import serializers

from accounts.api.serializers import BaseUserSerializer
from photos.serializers import ImageSerializer
from .models import Feed


class FeedSerializer(serializers.ModelSerializer):
    photo = ImageSerializer()
    latest_user = BaseUserSerializer()

    class Meta:
        model = Feed
        fields = ('feed_type', 'description', 'date_time', 'latest_user', 'photo')
