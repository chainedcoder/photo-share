from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

AUTH_TOKEN_EXPIRE_HOURS = getattr(
    settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 1)


class ExpiringTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        '''if token.created < timezone.now() - timedelta(hours=AUTH_TOKEN_EXPIRE_HOURS):
            raise exceptions.AuthenticationFailed('Token has expired')'''

        return (token.user, token)
