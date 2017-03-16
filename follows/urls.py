from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'request/$', request_follow, name="request-follow"),
    url(r'request-response/$', accept_request, name="accept-request"),
    url(r'requests/$', get_tink_requests, name="friend-requests"),
    url(r'get-friends/$', get_user_friends, name="get-friends"),
    url(r'delete-request/$', delete_request, name="delete-request"),
    url(r'unfollow/$', unfollow, name="unfollow"),
    url(r'follow/qrcode/(?P<user_id>\d+)/$', follow_qrcode, name="follow-qrcode")
]
