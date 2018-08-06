from hashlib import md5

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import ProfileVideo
from follows.utils import are_friends, friend_request_exists

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('public_id', 'username', 'first_name', 'last_name', 'bio', 'profile_pic', 'email')

    def to_representation(self, instance):
        res = super(BaseUserSerializer, self).to_representation(instance)
        profile_pic = res.get('profile_pic', None)
        email = res.get('email')
        if profile_pic is None:
            res['profile_pic'] = 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d&?r=pg' % (md5(email.encode('utf-8')).hexdigest(), 300)
        return res


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('public_id', 'username', 'email', 'first_name', 'last_name',
                  'bio', 'birthday', 'profile_pic', 'password')
        write_only_fields = ('password', )
        read_only_fields = ('public_id', 'profile_pic')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        res = super(UserSerializer, self).to_representation(instance)
        profile_pic = res.get('profile_pic', None)
        email = res.get('email')
        if profile_pic is None:
            res['profile_pic'] = 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d&?r=pg' % (md5(email.encode('utf-8')).hexdigest(), 300)
        return res


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


class ProfilePictureSerializer(serializers.Serializer):
    profile_pic = serializers.ImageField()

    class Meta:
        fields = ('profile_pic', )


class VideoUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileVideo
        fields = ('video_file', 'os_type')
        read_only_fields = ('id', )

    def create(self, validated_data):
        video = ProfileVideo(**validated_data)
        owner = validated_data.get('owner')
        video.owner = owner
        video.save()
        return video


class GeneralUserSerializer(BaseUserSerializer):
    is_friend = serializers.SerializerMethodField()
    friend_request_sent = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(GeneralUserSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user

    class Meta:
        model = User
        fields = ('public_id', 'username', 'first_name', 'last_name', 'bio', 'profile_pic',
                  'is_friend', 'friend_request_sent', 'email')

    def get_is_friend(self, obj):
        return are_friends(self.user, obj)

    def get_friend_request_sent(self, obj):
        return friend_request_exists(self.user, obj)
