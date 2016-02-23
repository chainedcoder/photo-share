import datetime

from django.shortcuts import render
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer

RESPONSE = {}


@api_view(['POST'])
def sign_up(request):
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid() and serialized.create(request.data, request):
        RESPONSE['msg'] = 'Account created successfully.'
        return Response(RESPONSE, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request):
    old_pass = request.data['old_password']
    new_pass = request.data['new_password']
    pass


@api_view(['GET'])
def profile(request):
    pass


class ObtainExpiringAuthToken(ObtainAuthToken):

    def post(self, request):
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
            RESPONSE['user'] = {
                'name': token.user.get_full_name(),
                'username': token.user.username}
            return Response(RESPONSE, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()
