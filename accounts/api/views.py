import json
from io import FileIO, BufferedWriter

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.mixins import (UpdateModelMixin, RetrieveModelMixin)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from accounts.models import ProfileVideo
from tink_api.settings import r
from .serializers import (UserSerializer, PasswordChangeSerializer, ProfilePictureSerializer,
                          VideoUploadSerializer, GeneralUserSerializer)

User = get_user_model()


class CreateUser(CreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Registers a new user
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # login user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            jwt_response_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = jwt_response_handler(token, user)

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def check_credential_availability(request):
    if 'email' in request.query_params and request.query_params.get('email') is not None:
        try:
            User.objects.get(email=request.query_params['email'])
            return Response({'available': False})
        except ObjectDoesNotExist:
            return Response({'available': True})
    if 'username' in request.query_params and request.query_params.get('username') is not None:
        try:
            User.objects.get(username=request.query_params['username'])
            return Response({'available': False})
        except ObjectDoesNotExist:
            return Response({'available': True})
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def check_password(request):
    password = request.data['password']
    user = request.user
    if user.check_password(password):
        return Response({'valid': True})
    else:
        return Response({'valid': False})


class UserList(ListAPIView):
    serializer_class = GeneralUserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.query_params.get('q', None)
        users = []
        if q is not None:
            users = User.objects.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q)
            ).exclude(pk=self.request.user.pk)
        return users

    def paginate_queryset(self, queryset):
        return None


class Profile(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    queryset = User.objects.all()
    lookup_field = 'public_id'
    lookup_url_kwarg = 'public_id'

    def get(self, request, *args, **kwargs):
        """
        Returns a user's profile
        """
        return self.retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        user = self.get_object()
        request_user = self.request.user

        if user == request_user:
            return UserSerializer
        else:
            return GeneralUserSerializer

    def patch(self, request, public_id):
        """
        Updates a user's profile - name, birthday, bio
        """
        user = self.get_object()
        if user is not None and user == request.user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordChange(UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    model = User

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            current_password = serializer.data['current_password']
            new_password = serializer.data['new_password']

            # check if current password is valid
            if not obj.check_password(current_password):
                return Response({'msg': 'Invalid current password'}, status=status.HTTP_401_UNAUTHORIZED)

            obj.set_password(new_password)
            obj.save(update_fields=['password'])
            return Response({'msg': 'Password updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfilePicture(UpdateAPIView):
    parser_classes = (MultiPartParser, FormParser, )
    serializer_class = ProfilePictureSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            profile_pic = request.data['profile_pic']
            user.profile_pic.save(profile_pic.name, profile_pic)
            return Response({'profile_pic': request.build_absolute_uri(user.profile_pic.url)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoUpload(APIView):
    serializer_class = VideoUploadSerializer
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            profile_video = serializer.save(user=request.user)

            pub_msg = {
                "task_type": 1,
                "user_id": request.user.pk,
                "video_path": '/opt/tink_api_v2/tink_api' + profile_video.video_file.url,
                "os_type": profile_video.os_type
            }

            r.publish('recognition_tasks', json.dumps(pub_msg))

            return Response({}, status=201)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_qr_code(request):
    return Response({'qr_code': request.user.tink_qrcode.url})

