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

    class Meta:
        model = User
        fields = ('password', 'first_name', 'last_name', 'email', 'username')
        write_only_fields = ('password', )
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'id')

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
            print e
            return False
