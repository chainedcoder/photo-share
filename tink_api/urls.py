"""tink_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^', include('core.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^friends/', include('follows.urls')),
    url(r'^photos/', include('photos.urls')),
]

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^media/(?P<path>.*)$',
                                    'django.views.static.serve',
                                    {'document_root': settings.MEDIA_ROOT, }),
                            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.STATIC_ROOT, }),
                            )