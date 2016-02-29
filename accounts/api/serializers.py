import hashlib
import datetime
import random

from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils import timezone

from rest_framework import serializers

from notifications.models import Notification
from notifications.tasks import send_notifications

from accounts.models import CustomUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields['username'].error_messages['unique'] = 'That username already exists.'

    name = serializers.CharField(
        source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'username')
        write_only_fields = ('password', 'first_name', 'last_name')

    def create(self, validated_data, request):
        try:
            first_name = validated_data['first_name']
            last_name = validated_data['last_name']
            email = validated_data['email']
            user = User.objects.create(
                username=validated_data['username'],
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(validated_data['password'])
            # Generate a unique activation link and save
            random_string = str(random.random()).encode('utf8')
            salt = hashlib.sha1(random_string).hexdigest()[:5]
            salted = (salt + email).encode('utf8')
            email_verification_key = hashlib.sha1(salted).hexdigest()
            user.email_verification_key = email_verification_key
            email_verification_key_expires = timezone.now() + datetime.timedelta(14)
            user.email_verification_key_expires = email_verification_key_expires
            user.save()
            # create notification to verify email
            notification = Notification.objects.create(mode=1)
            notification.recipient = user
            content = get_template('notifications/new_account.txt')
            d = {
                'first_name': first_name,
                'email_verification_key': email_verification_key,
            }
            notification.subject = 'Confirm your Tink Account'
            notification.content = content.render(d, request)
            notification.save()
            send_notifications.delay()
            return True
        except Exception, e:
            return False

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        confirm_password = validated_data.get('confirm_password', None)
        '''if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()
        update_session_auth_hash(self.context.get('request'), instance)'''
        instance.save()
        return instance
