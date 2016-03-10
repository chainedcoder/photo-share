import datetime

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes((AllowAny, ))
def sign_up(request):
    RESPONSE = {}
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid() and serialized.create(request.data, request):
        RESPONSE['msg'] = 'Account created successfully.'
        return Response(RESPONSE, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request):
    RESPONSE = {}
    user = request.user
    old_pass = request.data['old_password']
    if user.check_password(old_pass):
        new_pass = request.data['new_password']
        user.set_password(new_pass)
        user.save()
        RESPONSE['msg'] = 'Password changed successfully.'
        status_code = status.HTTP_200_OK
    else:
        RESPONSE['msg'] = 'Invalid password!'
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(RESPONSE, status=status_code)


@api_view(['GET'])
def my_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


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
        return Response(RESPONSE, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        RESPONSE['msg'] = 'User does not exist!'
        return Response(RESPONSE, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def edit_profile(request):
    RESPONSE = {}
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(user, request.data)
        RESPONSE['msg'] = 'Profile updated successfully.'
        status_code = status.HTTP_200_OK
    else:
        RESPONSE['msg'] = 'Error updating profile.'
        RESPONSE['errors'] = serializer.errors
        status_code = status.HTTP_200_OK
    return Response(RESPONSE, status=status_code)


@api_view(['GET'])
def search(request):
    q = request.query_params['query']
    users = User.objects.filter(Q(first_name__icontains=q) | Q(
        last_name__icontains=q) | Q(username__icontains=q))
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


class ObtainExpiringAuthToken(ObtainAuthToken):

    def post(self, request):
        RESPONSE = {}
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(
                user=serializer.validated_data['user'])
            date_time = timezone.now()
            if not created and token.created < date_time - datetime.timedelta(hours=1):
                token.delete()
                token = Token.objects.create(
                    user=serializer.validated_data['user'])
                token.created = timezone.now()
                token.save()
            RESPONSE['token'] = token.key
            user = token.user
            profile_pic = None
            if user.profile_pic:
                profile_pic = user.profile_pic.url
            RESPONSE['user'] = {
                'name': user.get_full_name(),
                'profile_pic': profile_pic,
                'username': user.username}
            return Response(RESPONSE, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()
