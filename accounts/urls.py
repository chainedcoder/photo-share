from django.conf.urls import url

from rest_framework.authtoken import views as drf_views

from .views import *
from .api.views import *

urlpatterns = [
    url(r'sign-up/$', sign_up, name="sign-up"),
    url(r'verify-email/(?P<email_verification_key>\w+)/$',
        verify_email, name="verify-email"),
    # url(r'sign-in/', drf_views.obtain_auth_token),
    url(r'sign-in/$', obtain_expiring_auth_token),
    url(r'my-profile/$', my_profile, name="my-profile"),
    url(r'profile/$', profile, name="profile"),
    url(r'profile/edit/', edit_profile, name="edit-profile"),
]
