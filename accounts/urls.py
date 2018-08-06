from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from . import views
from .api.views import (UserList, CreateUser, Profile, PasswordChange, UpdateProfilePicture,
                        VideoUpload, check_credential_availability, check_password)

urlpatterns = [
    url(r'sign-up/$', CreateUser.as_view()),
    url(r'check-credential-availability/', check_credential_availability),
    url(r'sign-in/$', obtain_jwt_token),
    url(r'users/$', UserList.as_view()),
    url(r'users/(?P<public_id>[0-9a-f-]+)/$', Profile.as_view()),
    url(r'change-password/$', PasswordChange.as_view()),
    url(r'check-password/$', check_password),

    url(r'update-profile-picture/$', UpdateProfilePicture.as_view()),
    url(r'new-video/', VideoUpload.as_view(), name='new-video'),
    # password reset
    url(r'begin-password-reset/$', views.begin_password_reset,
        name='begin-password-reset'),
    url(r'password-reset-initiated/$', views.password_reset_initiated,
        name='password-reset-initiated'),
    url(r'password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.reset_password,
        name='password-reset'),
    url(r'password-reset-complete/$', views.reset_password_complete,
        name='password-reset-complete'),
]
