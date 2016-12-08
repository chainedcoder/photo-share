from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from .api.views import (sign_up, account_detail, update_profile_picture, search, VideoUpload,
                        update_password, update_profile)

urlpatterns = [
    url(r'sign-up/$', sign_up, name="sign-up"),
    url(r'sign-in/$', obtain_jwt_token),
    url(r'(?P<pk>\d+)/$', account_detail),
    url(r'update-profile-picture/$', update_profile_picture),
    url(r'change-password/$', update_password),
    url(r'upload-video/', VideoUpload.as_view(), name='upload-video'),
    url(r'update-profile/', update_profile, name='update-profile'),
    url(r'search/', search, name='search'),
]
