from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from .views import *


schema_view = get_swagger_view(title='Tink API')

urlpatterns = [
    url(r'^$', APIHome.as_view(), name="home"),
    url(r'docs/', schema_view),
]
