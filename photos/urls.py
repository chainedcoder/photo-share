from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^photo/$', upload_photo, name='photo-list'),
    url(r'^photo/(?P<pk>[0-9]+)/$', PhotoDetail.as_view(), name='photo-detail')
]