from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^photo/$', upload_photo, name='photo-list'),
    url(r'^photo/(?P<pk>[0-9]+)/$', PhotoDetail.as_view(), name='photo-detail'),
    url(r'^photo-stream/$', photo_stream, name='photo-stream'),
    url(r'^pending-outbox/$', sample_outbox_pending, name='pending-outbox'),
    url(r'^sent-outbox/$', sample_outbox_sent, name='sent-outbox'),
    url(r'^user-photos/$', sample_photos, name='user-photos'),
]
