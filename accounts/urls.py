from django.conf.urls import url

from .api.views import (sign_up, obtain_expiring_auth_token, search, VideoUpload,
                        update_profile)

urlpatterns = [
    url(r'sign-up/$', sign_up, name="sign-up"),
    url(r'sign-in/$', obtain_expiring_auth_token),
    url(r'upload-video/', VideoUpload.as_view(), name='upload-video'),
    url(r'update-profile/', update_profile, name='update-profile'),
    url(r'search/', search, name='search'),
]
