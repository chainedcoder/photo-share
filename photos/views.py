import os
import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from .models import UploadedPhoto

User = get_user_model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@api_view(['POST'])
def upload_photo(request):
    RESPONSE = {}
    serializer = PhotoSerializer(data=request.data)
    if serializer.is_valid():
        photo = UploadedPhoto(
            image=serializer.validated_data['image'], owner=request.user)
        photo.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def photo_stream(request):
    with open(BASE_DIR + '/photos/sample.json') as data_file:
        data = json.load(data_file)
    return Response(data)


class PhotoList(APIView):

    def get(self, request, format=None):
        photo = UploadedPhoto.objects.all()
        serializer = PhotoSerializer(photo, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PhotoDetail(APIView):

    def get_object(self, pk):
        try:
            return UploadedPhoto.objects.get(pk=pk)
        except UploadedPhoto.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        photo = self.get_object(pk)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def pre_save(self, obj):
        obj.owner = self.request.user
