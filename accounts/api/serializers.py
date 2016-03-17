import hashlib
import datetime
import random
from base64 import b64decode

from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils import timezone
from django.core.files.base import ContentFile

from rest_framework import serializers

from notifications.models import Notification
from notifications.tasks import send_notifications

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        source='get_full_name', read_only=True)
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'name', 'username', 'profile_pic_url', 'website', 'bio')
        write_only_fields = ('password', 'first_name', 'last_name')

    def get_profile_pic_url(self, obj):
        return obj.get_profile_pic()

    def create(self, validated_data, request):
        try:
            first_name = validated_data.get('first_name')
            last_name = validated_data.get('last_name')
            email = validated_data['email']
            bio = validated_data.get('bio')
            facebook_id = validated_data.get('facebook_id')
            birthday = validated_data.get('birthday')
            if birthday is not None:
                bday_date_str = datetime.datetime.strptime(
                    birthday, "%m/%d/%Y").strftime("%Y-%m-%d")
                bday_date = datetime.datetime.strptime(
                    bday_date_str, "%Y-%m-%d")
            user = User.objects.create(
                username=validated_data['username'],
                email=email,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                facebook_id=facebook_id,
                birthday=bday_date
            )
            user.set_password(validated_data['password'])
            # Generate a unique activation link and save
            random_string = str(random.random()).encode('utf8')
            salt = hashlib.sha1(random_string).hexdigest()[:5]
            salted = (salt + email).encode('utf8')
            email_verification_key = hashlib.sha1(salted).hexdigest()
            user.email_verification_key = email_verification_key
            email_verification_key_expires = timezone.now(
            ) + datetime.timedelta(14)
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
            notification.subject = 'Confirm your tink email address'
            notification.content = content.render(d, request)
            notification.save()
            send_notifications.delay()
            return True
        except Exception, e:
            print e
            return False

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.website = validated_data.get('website', instance.website)
        bday = validated_data.get('birthday')
        if bday is not None:
            bday_date = datetime.datetime.strptime(bday, "%Y-%m-%d")
            instance.birthday = bday_date
        profile_pic = validated_data.get('profile_pic')
        if profile_pic is not None:
            file_name = 'ppic_%s.jpg' % instance.pk
            image_data = b64decode(profile_pic)
            instance.profile_pic = ContentFile(image_data, file_name)
        instance.save()
        return instance
