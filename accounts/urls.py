from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from .api.views import (sign_up, search, VideoUpload,
                        update_profile)

urlpatterns = [
    url(r'sign-up/$', sign_up, name="sign-up"),
    url(r'sign-in/$', obtain_jwt_token),
    url(r'upload-video/', VideoUpload.as_view(), name='upload-video'),
    url(r'update-profile/', update_profile, name='update-profile'),
    url(r'search/', search, name='search'),
]
