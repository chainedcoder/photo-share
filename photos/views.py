import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, When, Case, IntegerField, Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.mixins import (UpdateModelMixin, RetrieveModelMixin)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from core.utils import SmallResultsSetPagination
from feed.models import Feed
from follows.models import Follow
from tink_api.settings import r
from .models import UploadedPhoto, PhotoStream, PhotoStreamPhoto
from .serializers import (ImageSerializer, MainFeedSerializer, OutboxFeedBaseSerializer,
                          OutboxFeedSerializer, FeedPhotoSerializer, OutboxImageSendSerializer, OutboxSentSerializer)

User = get_user_model()


class UploadPhoto(CreateAPIView):
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request, *args, **kwargs):
        """
        Uploads a new photo
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(owner=request.user)

            # publish to redis for recognition purposes
            pub_msg = {
                "task_type": 2,
                "username": request.user.username,
                "image_path": '/opt/tink_api_v2/tink_api' + photo.image.url,
                "photo_id": photo.pk
            }

            r.publish('recognition_tasks', json.dumps(pub_msg))

            return Response({}, status=201)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MainFeed(ListAPIView):
    """
    Returns a user's photo feed
    """
    serializer_class = MainFeedSerializer
    pagination_class = SmallResultsSetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return PhotoStream.objects.annotate(
            photo_count=Sum(
                Case(When(images__deleted=False, images__send_photo=True, then=1), output_field=IntegerField()))
        ).filter(to_user=self.request.user, photo_count__gte=1).select_related('from_user')


@api_view(['PATCH'])
def mark_feed_seen(request, public_id):
    try:
        ps = PhotoStream.objects.get(public_id=public_id)
        ps.seen = True
        ps.save(update_fields=['seen'])
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class StreamDetail(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    serializer_class = MainFeedSerializer
    queryset = PhotoStream.objects.all()
    lookup_url_kwarg = 'public_id'
    lookup_field = 'public_id'

    @staticmethod
    def get_stream(public_id):
        try:
            return PhotoStream.objects.get(public_id=public_id)
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, public_id):
        """
        Updates a feed item - mainly for now updating seen status
        """
        stream = self.get_stream(public_id)
        if stream:
            serializer = self.serializer_class(
                stream, data=request.data, partial=True)
            if serializer.is_valid():
                return Response(status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


class StreamPhotoList(ListAPIView):
    serializer_class = FeedPhotoSerializer

    @staticmethod
    def get_feed(public_id):
        try:
            return PhotoStream.objects.get(public_id=public_id)
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        feed = self.get_feed(self.kwargs['public_id'])
        if feed is not None:
            return feed.images.all()
        return []

    def paginate_queryset(self, queryset):
        return None


@api_view(['PATCH'])
def like_photo(request, public_id):
    try:
        photo = PhotoStreamPhoto.objects.get(public_id=public_id)
        photo.liked = not photo.liked
        photo.save(update_fields=['liked'])
        user = request.user
        photo_id = photo.photo.public_id
        # create feed
        if photo.liked:
            try:
                # check if pic has been liked by user before
                Feed.objects.get(photo__public_id=photo_id, user_to=user)
            except ObjectDoesNotExist:
                try:
                    photo = UploadedPhoto.objects.get(public_id=photo_id)
                    description = '{} likes your photo.'.format(user.username)
                    feed = Feed(feed_type=1, user_to=photo.owner, description=description, photo=photo,
                                latest_user=user)
                    feed.save()
                except ObjectDoesNotExist:
                    pass
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def delete_photo(request, public_id):
    try:
        photo = PhotoStreamPhoto.objects.get(public_id=public_id)
        photo.deleted = True
        photo.save(update_fields=['deleted'])
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserPhotos(ListAPIView):
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        # get all streams that were to user
        photos = UploadedPhoto.objects.filter(
            pk__in=PhotoStreamPhoto.objects.filter(
                stream__to_user=user, liked=True, deleted=False).values_list('photo_id', flat=True)
        ).select_related('owner')
        return photos


class FriendPhotos(ListAPIView):
    serializer_class = FeedPhotoSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = []
        movement = self.request.query_params.get('movement')
        other_user = self.get_user(self.kwargs['public_id'])
        user = self.request.user

        if movement is not None and user is not None:
            if movement == 'in':
                queryset = PhotoStreamPhoto.objects.filter(stream__to_user=user, deleted=False,
                                                           stream__from_user=other_user).select_related('photo')
            elif movement == 'out':
                queryset = PhotoStreamPhoto.objects.filter(stream__to_user=other_user, deleted=False,
                                                           stream__from_user=user).select_related('photo')
        return queryset

    @staticmethod
    def get_user(public_id):
        try:
            return User.objects.get(public_id=public_id)
        except ObjectDoesNotExist:
            return None


class LikedPhotosList(ListAPIView):
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            user_1 = User.objects.get(public_id=user_id)
            user_2 = self.request.user
            queryset = UploadedPhoto.objects.filter(Q(photostreamphoto__stream__from_user=user_1, photostreamphoto__stream__to_user=user_2) | Q(
                photostreamphoto__stream__from_user=user_2, photostreamphoto__stream__to_user=user_1), photostreamphoto__liked=True).select_related('owner')
            return queryset
        return []


class OutboxFeed(ListAPIView):
    """
    Returns a user's outbox feed - photos from user to other users
    """
    serializer_class = OutboxFeedSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return PhotoStream.objects.annotate(
            photo_count=Sum(
                Case(When(images__send_photo=False, images__deleted=False, then=1), output_field=IntegerField()))
        ).filter(from_user=self.request.user, send_all_photos=False, photo_count__gte=1).select_related('to_user')


@api_view(['POST'])
def send_all_photos_in_feed(request, public_id):
    try:
        feed = PhotoStream.objects.prefetch_related('images').get(public_id=public_id)
        feed.send_all_photos = True
        feed.save(update_fields=['send_all_photos'])
        feed.images.update(send_photo=True)
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def send_photos_in_outbox(request):
    serializer = OutboxImageSendSerializer(data=request.data, many=True)
    if serializer.is_valid():
        public_idx = [i['photo_id'] for i in serializer.validated_data]
        PhotoStreamPhoto.objects.filter(public_id__in=public_idx).update(send_photo=True)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class OutboxSentFeed(ListAPIView):
    serializer_class = OutboxSentSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = PhotoStream.objects.filter(from_user=self.request.user).select_related('from_user').prefetch_related(
            'images')
        return queryset


@api_view(['GET'])
def get_num_shares(request, public_id):
    try:
        other_user = User.objects.get(public_id=public_id)
        user = request.user
        shares_in = PhotoStreamPhoto.objects.filter(
            stream__from_user=other_user, stream__to_user=user
        ).count()
        shares_out = PhotoStreamPhoto.objects.filter(
            Q(stream__from_user=user, stream__to_user=other_user)
        ).count()
        return Response({'shares_in': shares_in, 'shares_out': shares_out})
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def test_auto_send(request, user_from, user_to):
    return Response({'autosend': Follow.check_auto_send(user_from, user_to)})
