import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from notifications.models import Notification
from notifications.tasks import send_notifications
from accounts.api.serializers import UserSerializer

from tink_api.settings import BASE_DIR
from .models import Follow
from .serializers import *

User = get_user_model()


@api_view(['POST'])
def request_follow(request):
    RESPONSE = {}
    # user performing the action
    request_from = request.user
    try:
        request_to = User.objects.get(pk=request.data['user_id'])
        if request_from == request_to:
            RESPONSE['msg'] = 'Oops, an error occurred!'
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                Follow.objects.get(Q(user_1=request_from, user_2=request_to) | Q(
                    user_1=request_to, user_2=request_from))
                RESPONSE['msg'] = 'You are already tinked with this person!'
                status_code = status.HTTP_400_BAD_REQUEST
            except ObjectDoesNotExist:
                follow = Follow(user_1=request_from, user_2=request_to)
                follow.save()
                # notify request_to
                notification = Notification.objects.create(mode=2)
                notification.subject = 'New Tink Request'
                content = get_template('notifications/new_tink_request.txt')
                d = {
                    'request_from': request_from.get_full_name()
                }
                notification.content = content
                notification.recipient = request_to
                notification.save()
                send_notifications.delay()
                RESPONSE['msg'] = 'Request sent.'
                status_code = status.HTTP_201_CREATED
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'User does not exist!'
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['POST'])
def follow_qrcode(request, user_id):
    RESPONSE = {}
    scanner = request.user
    scanee = User.objects.get(pk=user_id)
    if scanner == scanee:
        RESPONSE['msg'] = "Could not complete action."
        RESPONSE['status_code'] = 1
    else:
        try:
            follow = Follow.objects.get(Q(user_1=scanner, user_2=scanee) | Q(
                user_1=scanee, user_2=scanner))
            RESPONSE['msg'] = 'You are already tinked with this person!'
            if not follow.date_accepted:
                RESPONSE['msg'] = 'A tink request is pending confirmation.'
            RESPONSE['status_code'] = 1
        except ObjectDoesNotExist:
            follow = Follow(user_1=scanner, user_2=scanee, status=1,
                            date_accepted=timezone.now())
            follow.save()
            RESPONSE['msg'] = 'Successfully tinked with {0}'.format(scanee.get_full_name())
            RESPONSE['status_code'] = 0
    return Response(RESPONSE)


@api_view(['GET'])
def get_tink_requests(request):
    user = request.user
    requests = Follow.objects.filter(status=0, user_2=user)
    serializer = FollowRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def accept_request(request):
    RESPONSE = {}
    request_id = request.data['request_id']
    try:
        follow = Follow.objects.get(pk=request_id, status=0)
        follow.status = 1
        follow.date_accepted = timezone.now()
        follow.save()
        # send requestor notification
        RESPONSE['msg'] = 'Tink request accepted.'
        status_code = status.HTTP_200_OK
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'Request does not exist.'
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['POST'])
def delete_request(request):
    RESPONSE = {}
    request_id = request.data['request_id']
    try:
        follow = Follow.objects.get(pk=request_id, status=0)
        follow.delete()
        # send requestor notification
        RESPONSE['msg'] = 'Tink request removed.'
        status_code = status.HTTP_200_OK
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'Request does not exist.'
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['POST'])
def unfollow(request):
    RESPONSE = {}
    request_from = request.user
    request_to = get_object_or_404(User, pk=request.data('user_id'))
    try:
        follow = Follow.objects.get(Q(user_1=request_from, user_2=request_to) | Q(
            user_1=request_from, user_2=request_to))
        follow.delete()
        RESPONSE['msg'] = 'Successfully untinked {0}'.format(
            unfriend.username)
        status_code = status.HTTP_201_CREATED
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'You are not tinked with this person.'
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_user_friends(request):
    '''user = request.user
    friends = user.get_user_friends()
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data)'''
    with open(BASE_DIR + '/follows/sample_friends.json') as data_file:
        data = json.load(data_file)
    return Response(data)


@api_view(['POST'])
def block_user(request):
    pass


@api_view(['POST'])
def unblock_user(request):
    pass
