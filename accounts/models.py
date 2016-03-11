from __future__ import unicode_literals
from itertools import chain
from cStringIO import StringIO

import qrcode

from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

from follows.models import Follow


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    username = models.CharField(_('username'), max_length=20, unique=True)
    first_name = models.CharField(
        _('first name'), max_length=30, null=True)
    last_name = models.CharField(
        _('last name'), max_length=30, null=True)
    phone_regex = RegexValidator(
        regex=r'^[0-9]{9,15}$', message="Enter a valid phone number (9 - 15 digits).")
    phone_number = models.CharField(
        _('phone number'), max_length=30, null=True, validators=[phone_regex])
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    email_verification_key = models.CharField(
        max_length=40, blank=True, null=True)
    email_verification_key_expires = models.DateTimeField(
        blank=True, null=True)
    phone_verification_code = models.IntegerField(blank=True, null=True)
    phone_verification_code_expires = models.DateTimeField(
        blank=True, null=True)
    account_verified_date = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(_('last seen'), blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True)
    tink_qrcode = models.ImageField(upload_to='tink_qrcodes', null=True)
    bio = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True)
    website = models.URLField(null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['id']
        default_permissions = ()

    def __str__(self):
        return str(self.get_full_name())

    def get_absolute_url(self):
        return reverse('users', kwargs={'pk': self.pk})

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_profile_pic(self):
        """
        Returns user profile pic or default one
        """
        if not self.profile_pic:
            return "https://thesocietypages.org/socimages/files/2009/05/nopic_192.gif"
        else:
            return self.profile_pic.url

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_user_friends(self):
        friends = Follow.objects.filter(Q(user_1=self) | Q(user_2=self))
        a = []
        for friend in friends:
            if friend.user_1 == self:
                c = friend.user_2
            elif friend.user_2 == self:
                c = friend.user_1
            a.append(c)
        return a

    def are_friends(self, other_user):
        try:
            Follow.objects.get(
                Q(user_1=self, user_2=other_user) | Q(user_2=self, user_1=other_user))
            return True
        except ObjectDoesNotExist:
            return False

    def post_save_receiver(sender, instance, **kwargs):
        if not instance.tink_qrcode:
            # generate their qr code
            qr = qrcode.QRCode(version=1,
                               error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=10,
                               border=4
                               )
            qr_data = str(
                reverse('follow-qrcode', kwargs={'user_id': instance.pk}))
            qr.add_data(qr_data)
            qr.make(fit=True)
            image = qr.make_image()

            # save image to string buffer
            image_buffer = StringIO()
            image.save(image_buffer, format='JPEG')
            image_buffer.seek(0)

            # Here we use django file storage system to save the image.
            file_name = 'QR_%s.jpg' % instance.pk
            file_object = File(image_buffer, file_name)
            content_file = ContentFile(file_object.read())
            instance.tink_qrcode.save(file_name, content_file, save=True)

    models.signals.post_save.connect(
        post_save_receiver, sender=settings.AUTH_USER_MODEL)
