import os
import json
from io import FileIO, BufferedWriter

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from tink_api.settings import BASE_DIR, MEDIA_ROOT, MEDIA_FOLDER_NAME, r

from .serializers import PhotoSerializer, PhotoStreamSerializer
from .models import UploadedPhoto, PhotoStream

User = get_user_model


class UploadPhoto(APIView):
    serializer_class = PhotoSerializer
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request):
        uploaded_image = request.data['image_file']
        uploads_dir = os.path.join(MEDIA_ROOT, 'uploads/user_photos')
        if not os.path.isdir(uploads_dir):
            os.makedirs(uploads_dir)

        dest_file_path = os.path.join(uploads_dir, uploaded_image.name)

        with BufferedWriter(FileIO(dest_file_path, "wb")) as runtime_file:
            for c in uploaded_image.chunks():
                runtime_file.write(c)

        rel_path = 'uploads/user_photos/' + uploaded_image.name

        photo = UploadedPhoto.objects.create(
            owner=request.user,
            image=rel_path)

        pub_msg = {
            "task_type": 2,
            "username": request.user.username,
            "image_path": dest_file_path,
            "photo_id": photo.pk
        }

        r.publish('recognition_tasks', json.dumps(pub_msg))

        return Response({}, status=201)


@api_view(['GET', 'PATCH'])
def photo_stream(request):
    if request.method == 'GET':
        stream = PhotoStream.objects.filter(to_user=request.user).prefetch_related()
        serializer = PhotoStreamSerializer(stream, many=True)
        return Response(serializer.data)


@api_view(['PATCH'])
def mark_stream_seen(request, stream_id):
    try:
        stream = PhotoStream.objects.get(pk=stream_id)
        stream.seen = True
        stream.save(update_fields=['seen'])
        return Response({'status_code': 0})
    except ObjectDoesNotExist:
        return Response({'status_code': 1})


@api_view(['GET'])
@permission_classes((AllowAny, ))
def sample_photos(request):
    with open(BASE_DIR + '/photos/sample_photos.json') as data_file:
        data = json.load(data_file)
    return Response(data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def sample_outbox_pending(request):
    with open(BASE_DIR + '/photos/sample_pending_outbox.json') as data_file:
        data = json.load(data_file)
    return Response(data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def sample_outbox_sent(request):
    with open(BASE_DIR + '/photos/sample_sent_outbox.json') as data_file:
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
