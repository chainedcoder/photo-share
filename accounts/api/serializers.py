from django.contrib.auth import get_user_model

from rest_framework import serializers

from accounts.models import ProfileVideo

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    ppic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'birthday', 'ppic_url')
        write_only_fields = ('password', )
        read_only_fields = ('id', )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def get_ppic_url(self, obj):
        return obj.get_profile_pic()


class VideoUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileVideo
        fields = ('video_file', )
        read_only_fields = ('id', )


