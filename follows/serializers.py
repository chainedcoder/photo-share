from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


class FollowRequestSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.IntegerField(
        source='user_1.id', read_only=True)
    username = serializers.CharField(
        source='user_1.username', read_only=True)
    name = serializers.CharField(
        source='user_1.get_full_name', read_only=True)
    ppic_url = serializers.CharField(source='user_1.get_profile_pic')

    class Meta:
        model = Follow
        fields = ('id', 'user_id', 'username', 'name', 'ppic_url')


class FriendSerializer(serializers.ModelSerializer):
    ppic_url = serializers.SerializerMethodField()
    autosend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'bio', 'ppic_url', 'autosend')
        write_only_fields = ('password', )
        read_only_fields = ('id', )

    def get_ppic_url(self, obj):
        return obj.get_profile_pic()

    def get_autosend(self, obj):
        # self.context.get("user_id")
        return True
