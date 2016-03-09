from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', APIHome.as_view(), name="home"),
]
