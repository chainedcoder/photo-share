from rest_framework import serializers

from .models import UploadedPhoto


class PhotoSerializer(serializers.ModelSerializer):
    owner = serializers.Field(source='owner.username', required=False)

    class Meta:
        model = UploadedPhoto
        fields = ('id', 'image', 'owner', 'time_uploaded')
        read_only_fields = ('id', )
