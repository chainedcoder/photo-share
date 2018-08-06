from rest_framework import serializers

from accounts.api.serializers import BaseUserSerializer
from .models import UploadedPhoto, PhotoStream, PhotoStreamPhoto


class BaseImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadedPhoto
        fields = ('image', 'time_uploaded', 'public_id')
        read_only_fields = ('time_uploaded', 'public_id')

    def create(self, validated_data):
        image = UploadedPhoto(**validated_data)
        owner = validated_data.get('owner')
        image.owner = owner
        image.save()
        return image


class ImageSerializer(serializers.ModelSerializer):

    owner = BaseUserSerializer(read_only=True)

    class Meta:
        model = UploadedPhoto
        fields = ('image', 'owner', 'time_uploaded', 'public_id')
        read_only_fields = ('time_uploaded', 'public_id')


class FeedPhotoSerializer(serializers.ModelSerializer):
    photo = BaseImageSerializer()

    class Meta:
        model = PhotoStreamPhoto
        fields = ('photo', 'liked', 'deleted', 'public_id')
        write_only_fields = ('deleted', )


class MainFeedSerializer(serializers.ModelSerializer):
    from_user = BaseUserSerializer()
    num_photos = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStream
        fields = ['public_id', 'from_user',
                  'num_photos', 'date_time', 'seen', 'images']

    @staticmethod
    def get_num_photos(obj):
        return obj.images.filter(deleted=False, send_photo=True).count()

    def get_images(self, obj):
        images = PhotoStreamPhoto.objects.filter(stream=obj, deleted=False, send_photo=True).select_related('photo')
        serializer = FeedPhotoSerializer(instance=images, many=True, context={'request': self.context['request']})
        return serializer.data


class OutboxFeedBaseSerializer(serializers.ModelSerializer):
    to_user = BaseUserSerializer()
    num_photos = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStream
        fields = ['public_id', 'to_user', 'num_photos', 'date_time']

    @staticmethod
    def get_num_photos(obj):
        return obj.images.filter(deleted=False, send_photo=False).count()


class OutboxSentSerializer(serializers.ModelSerializer):
    to_user = BaseUserSerializer()
    num_photos = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStream
        fields = ['public_id', 'to_user', 'num_photos', 'date_time']

    @staticmethod
    def get_num_photos(obj):
        return obj.images.filter(deleted=False, send_photo=True).count()


class OutboxFeedSerializer(OutboxFeedBaseSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStream
        fields = ['public_id', 'to_user', 'num_photos', 'date_time', 'images']

    def get_images(self, obj):
        images = PhotoStreamPhoto.objects.filter(stream=obj, deleted=False, send_photo=False).select_related('photo')
        serializer = FeedPhotoSerializer(instance=images, many=True, context={'request': self.context['request']})
        return serializer.data


class OutboxImageSendSerializer(serializers.Serializer):
    photo_id = serializers.UUIDField()
