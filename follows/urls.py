from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'request-follow/$', request_follow, name="request-follow"),
    url(r'accept-request/$', accept_request, name="accept-request"),
    url(r'get-tink-requests/$', get_tink_requests, name="get-requests"),
    url(r'get-followers/$', get_user_followers, name="get-followers"),
    url(r'delete-request/$', delete_request, name="delete-request"),
    url(r'unfollow/$', unfollow, name="unfollow"),
]
