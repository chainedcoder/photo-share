from rest_framework import serializers

from .models import Follow


class FollowRequestSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        source='user_1.username', read_only=True)
    name = serializers.CharField(
        source='user_1.get_full_name', read_only=True)
    ppic_url = serializers.CharField(source='user_1.get_profile_pic')

    class Meta:
        model = Follow
        fields = ('id', 'username', 'name', 'ppic_url')


class FriendSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        source='user.username', read_only=True)
    name = serializers.CharField(
        source='user.get_full_name', read_only=True)
    user_id = serializers.CharField(
        source='user.pk', read_only=True)

    class Meta:
        model = Follow
        fields = ('user_id', 'username', 'name')
