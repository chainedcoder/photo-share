from rest_framework import serializers

from .models import UploadedPhoto


class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username', required=False)

    class Meta:
        model = UploadedPhoto
        fields = ('id', 'image', 'owner')
