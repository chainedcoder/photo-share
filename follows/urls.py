from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.FriendList.as_view()),
    url(r'requests/count/$', views.get_num_friend_requests),
    url(r'count/$', views.get_num_friends),
    url(r'requests/$', views.FriendRequestList.as_view()),
    url(r'requests/(?P<public_id>[0-9a-f-]+)/$', views.FriendRequestDetail.as_view()),
    url(r'users/(?P<public_id>[0-9a-f-]+)/count/$', views.get_user_num_friends),
    url(r'(?P<user_id>[0-9a-f-]+)/toggle-auto-send/$', views.alter_auto_send),
    url(r'unfriend/(?P<user_id>[0-9a-f-]+)/$', views.unfriend)
]
