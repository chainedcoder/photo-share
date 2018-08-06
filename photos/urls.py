from django.conf.urls import url

from .views import (UploadPhoto, MainFeed, StreamDetail, StreamPhotoList, UserPhotos,
                    OutboxFeed, OutboxSentFeed, FriendPhotos, like_photo, mark_feed_seen,
                    delete_photo, get_num_shares, LikedPhotosList, send_all_photos_in_feed,
                    send_photos_in_outbox, test_auto_send)

urlpatterns = [
    url(r'streams/$', MainFeed.as_view()),
    url(r'streams/(?P<public_id>[0-9a-f-]+)/$', StreamDetail.as_view()),
    url(r'streams/(?P<public_id>[0-9a-f-]+)/photos/$',
        StreamPhotoList.as_view()),
    url(r'streams/(?P<public_id>[0-9a-f-]+)/seen/$', mark_feed_seen),
    url(r'outbox/$', OutboxFeed.as_view()),
    url(r'outbox/sent/$', OutboxSentFeed.as_view()),
    url(r'outbox/(?P<public_id>[0-9a-f-]+)/send-all-photos/$', send_all_photos_in_feed),
    url(r'outbox/send-photos/$', send_photos_in_outbox),
    url(r'new/$', UploadPhoto.as_view()),
    url(r'for-user/$', UserPhotos.as_view()),
    url(r'users/(?P<public_id>[0-9a-f-]+)/$', FriendPhotos.as_view()),
    url(r'(?P<public_id>[0-9a-f-]+)/like/$', like_photo),
    url(r'liked/$', LikedPhotosList.as_view()),
    url(r'(?P<public_id>[0-9a-f-]+)/delete/$', delete_photo),
    url(r'shared/user/(?P<public_id>[0-9a-f-]+)/$', get_num_shares),
    url(r'test-auto-send/(?P<user_from>\d+)/(?P<user_to>\d+)/$', test_auto_send)
]
