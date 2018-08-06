import itertools

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import (RetrieveModelMixin, UpdateModelMixin, ListModelMixin,
                                   CreateModelMixin)
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowRequestSerializer, FriendSerializer

User = get_user_model()


@api_view(['GET'])
def get_num_friend_requests(request):
    num = Follow.objects.filter(user_to=request.user, status=0).count()
    return Response({"friend_requests": num})


class FriendRequestList(ListModelMixin, CreateModelMixin, GenericAPIView):
    serializer_class = FollowRequestSerializer

    def get(self, request, *args, **kwargs):
        """
        Returns a list of friend requests for a user
        """
        return self.list(request, *args, **kwargs)

    def post(self, request):
        """
        Saves a new friend request
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user_from_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user_to=user, status=0).select_related('user_to')

    def paginate_queryset(self, queryset):
        return None


class FriendRequestDetail(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    serializer_class = FollowRequestSerializer
    queryset = Follow.objects.all()
    lookup_field = 'public_id'
    lookup_url_kwarg = 'public_id'

    def get(self, request, *args, **kwargs):
        """
        Returns details of a friend request
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, public_id):
        """
        Updates a friend request, mainly its status
        """
        req = self.get_friend_request(public_id)
        if req:
            serializer = self.serializer_class(req, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_friend_request(public_id):
        try:
            return Follow.objects.get(public_id=public_id)
        except ObjectDoesNotExist:
            return None


class FriendList(ListAPIView):
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        """
        Returns a list of a user's friends
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        idx = Follow.objects.filter(Q(status=1), Q(user_from=user) | Q(user_to=user)).values_list('user_from', 'user_to')
        user_idx = list(filter(lambda a: a != user.pk, list(itertools.chain.from_iterable(idx))))
        users = User.objects.filter(pk__in=user_idx).prefetch_related('user_from', 'user_to')
        return users


@api_view(['GET'])
def get_num_friends(request):
    user = request.user
    friends = Follow.objects.filter(
        Q(status=1), Q(user_from=user) | Q(user_to=user)
    ).count()
    return Response({"friends": friends})


@api_view(['GET'])
def get_user_num_friends(request, public_id):
    try:
        user = User.objects.get(public_id=public_id)
        friends = Follow.objects.filter(
            Q(status=1), Q(user_from=user) | Q(user_to=user)
        ).count()
        return Response({"friends": friends})
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def alter_auto_send(request, user_id):
    user = request.user
    other_user = User.objects.get(public_id=user_id)
    # find friendship
    try:
        friendship = Follow.objects.get(Q(user_from=user, user_to=other_user) | Q(user_to=user, user_from=other_user))
        if friendship.user_from == user:
            friendship.user_from_to_user_to = not friendship.user_from_to_user_to
        elif friendship.user_to == user:
            friendship.user_to_to_user_from = not friendship.user_to_to_user_from
        friendship.save(update_fields=['user_from_to_user_to', 'user_to_to_user_from'])
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def unfriend(request, user_id):
    user = request.user
    try:
        other_user = User.objects.get(public_id=user_id)
        try:
            friendship = Follow.objects.get(Q(user_from=user, user_to=other_user) | Q(user_from=other_user, user_to=user))
            friendship.status = 4
            friendship.save(update_fields=['status'])
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

