from rest_framework import serializers

from tink_api.settings import BASE_API_URL
from .models import UploadedPhoto, PhotoStream, PhotoStreamPhoto


class PhotoSerializer(serializers.ModelSerializer):
    owner = serializers.Field(source='owner.username', required=False)

    class Meta:
        model = UploadedPhoto
        fields = ('id', 'image', 'owner', 'time_uploaded')
        read_only_fields = ('id', )


class StreamPhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStreamPhoto
        fields = ('id', 'photo_url', 'liked')
        read_only_fields = ('id', )

    @staticmethod
    def get_photo_url(obj):
        return BASE_API_URL + obj.photo.image.url


class PhotoStreamSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='from_user.get_full_name')
    username = serializers.ReadOnlyField(source='from_user.username')
    profile_pic_url = serializers.ReadOnlyField(source='from_user.get_profile_pic')
    user_id = serializers.ReadOnlyField(source='from_user.pk')
    num_tinks = serializers.SerializerMethodField()
    images = StreamPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = PhotoStream
        read_only_fields = ('name', )
        fields = ['id', 'name', 'username', 'profile_pic_url', 'user_id',
                  'num_tinks', 'date_time', 'seen', 'images']

    @staticmethod
    def get_num_tinks(obj):
        return len(obj.images.all())
