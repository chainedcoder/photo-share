from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

from accounts.api.serializers import BaseUserSerializer
from .models import Follow

User = get_user_model()


class FollowRequestSerializer(serializers.ModelSerializer):
    user_from = BaseUserSerializer(required=False)
    user_to_id = serializers.UUIDField()

    class Meta:
        model = Follow
        fields = ('public_id', 'status', 'user_from', 'user_to_id')
        read_only_fields = ('public_id', 'user_from')
        write_only_fields = ('user_to_id', )

    @staticmethod
    def validate_user_to_id(value):
        try:
            user_to = User.objects.get(public_id=value)
            return user_to.pk
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid user")

    def validate(self, data):
        if not self.instance:
            # check if friend request already exists
            user_from_id = self.context['request'].user.pk
            user_to_id = data['user_to_id']
            try:
                Follow.objects.get(
                    Q(status=0), Q(user_from_id=user_from_id, user_to_id=user_to_id) | Q(user_from_id=user_to_id, user_to_id=user_from_id)
                )
                raise serializers.ValidationError('Friend request already sent')
            except ObjectDoesNotExist:
                pass
        return data

    def create(self, validated_data):
        req = Follow.objects.create(**validated_data)
        return req


class FriendSerializer(BaseUserSerializer):
    autosend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('public_id', 'username', 'first_name', 'last_name', 'bio', 'profile_pic', 'autosend', 'email')

    def get_autosend(self, obj):
        user = self.context['request'].user
        # get friendship
        friendship = Follow.objects.get(Q(user_from=obj, user_to=user) | Q(user_to=obj, user_from=user), status=1)
        if friendship.user_from == user:
            return friendship.user_from_to_user_to
        elif friendship.user_to == user:
            return friendship.user_to_to_user_from
