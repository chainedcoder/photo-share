from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy

from .views import *
from .api.views import *

urlpatterns = [
    url(r'sign-up/$', sign_up, name="sign-up"),
    url(r'verify-email/(?P<email_verification_key>\w+)/$',
        verify_email, name="verify-email"),
    url(r'sign-in/', obtain_expiring_auth_token),
]
