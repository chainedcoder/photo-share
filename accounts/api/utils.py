import datetime

from .serializers import UserSerializer


def jwt_payload_handler(user):
    """
    Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    return {
        'user_id': user.public_id,
        'email': user.email,
        'orig_iat': datetime.datetime.now().timetuple()
    }


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Custom response payload handler.
    This function controls the custom payload after login or token refresh. This data is returned through the web API.
    """
    res = UserSerializer(user, context={'request': request}).data
    res['token'] = token
    return res
