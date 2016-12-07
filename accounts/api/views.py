from io import FileIO, BufferedWriter
import json

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.files.temp import NamedTemporaryFile

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_jwt.settings import api_settings

from tink_api.settings import r

from accounts.models import ProfileVideo
from .serializers import UserSerializer, VideoUploadSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes((AllowAny, ))
def sign_up(request):
    response = dict()
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        user = serialized.create(request.data)
        # log in user
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response['token'] = token
        response['msg'] = 'Account created successfully.'
        response['status_code'] = 0
    else:
        response['status_code'] = 1
        response['msg'] = 'Something went wrong.'
        response['errors'] = serialized._errors
    return Response(response)


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


class VideoUpload(APIView):
    serializer_class = VideoUploadSerializer
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request, format=None):
        upload = request.data['video_file']
        fh = NamedTemporaryFile(delete=False)

        extension = upload.name.split(".")[1]
        filename = "{}.{}".format(fh.name, extension)

        with BufferedWriter(FileIO(filename, "w")) as dest:
            for c in upload.chunks():
                dest.write(c)

        profile_video = ProfileVideo.objects.create(
            user=request.user,
            video_file=filename)

        pub_msg = {
            "task_type": 1,
            "username": request.user.username,
            "video_path": profile_video.video_file.url
        }

        r.publish('recognition_tasks', json.dumps(pub_msg))

        return Response({}, status=201)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def check_fb_user_registered(request):
    try:
        User.objects.get(facebook_id=request.data['facebook_id'])
        return Response({'is_registered': True})
    except ObjectDoesNotExist:
        return Response({'is_registered': False})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def check_google_user_registered(request):
    try:
        User.objects.get(google_id=request.data['google_id'])
        return Response({'is_registered': True})
    except ObjectDoesNotExist:
        return Response({'is_registered': False})


@api_view(['POST'])
def change_password(request):
    RESPONSE = {}
    user = request.user
    old_pass = request.data['old_password']
    if user.check_password(old_pass):
        new_pass = request.data['new_password']
        user.set_password(new_pass)
        user.save()
        # update_session_auth_hash(self.context.get('request'), user)
        RESPONSE['msg'] = 'Password changed successfully.'
        RESPONSE['status_code'] = 0
        status_code = status.HTTP_200_OK
    else:
        RESPONSE['msg'] = 'Invalid password!'
        RESPONSE['status_code'] = 1
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['GET'])
def my_profile(request):
    RESPONSE = {}
    user = request.user
    serializer = UserSerializer(user)
    RESPONSE['user'] = serializer.data
    images = [
        {"url": "http://api.androidhive.info/feed/img/nat.jpg"},
        {"url": "http://api.androidhive.info/feed/img/time.png"},
        {"url": "http://api.androidhive.info/feed/img/lincoln.jpg"},
        {"url": "http://api.androidhive.info/feed/img/discovery.jpg"},
        {"url": "http://api.androidhive.info/feed/img/lincoln.jpg"},
        {"url": "http://api.androidhive.info/feed/img/ktm.png"}
    ]
    RESPONSE['images'] = images
    return Response(RESPONSE)


@api_view(['GET'])
def profile(request):
    RESPONSE = {}
    user_id = request.query_params['user_id']
    try:
        user = User.objects.get(pk=user_id)
        if user == request.user:
            return redirect(reverse('my-profile'))
        serializer = UserSerializer(user)
        RESPONSE['user'] = serializer.data
        RESPONSE['is_friend'] = request.user.are_friends(user)
        RESPONSE['status_code'] = 0
        return Response(RESPONSE, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'User does not exist!'
        RESPONSE['status_code'] = 1
        return Response(RESPONSE, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_profile(request):
    response = {}
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(user, request.data)
        response['msg'] = 'Profile updated successfully.'
        response['status_code'] = 0
    else:
        response['msg'] = 'Error updating profile.'
        response['errors'] = serializer.errors
        response['status_code'] = 1
    return Response(response)


@api_view(['GET'])
def search(request):
    q = request.query_params['query']
    users = User.objects.filter(Q(first_name__icontains=q) | Q(
        last_name__icontains=q) | Q(username__icontains=q))
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_qr_code(request):
    return Response({'qr_code': request.user.tink_qrcode.url})

