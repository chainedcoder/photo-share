from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from photos.models import UploadedPhoto
from photoshare.celery import app
from .models import Feed

User = get_user_model()


@app.task
def create_feed(feed_type, photo_id, user_id):
    user = User.objects.get(pk=user_id)
    if feed_type == 1:  # liked photo
        try:
            # check if pic has been liked before
            photo_liked = Feed.objects.get(photo__public_id=photo_id, user_to=user)
            # get number of users who already like the photo
            num_users = photo_liked.users.count()
            photo_liked.users.add(user_id)
            new_description = '{0} and {1} others like your photo.'.format(user.username, num_users)
            photo_liked.description = new_description
            photo_liked.date_time = timezone.now()
            photo_liked.latest_user = user
            photo_liked.save(update_fields=['description', 'date_time'])
        except ObjectDoesNotExist:
            try:
                photo = UploadedPhoto.objects.get(public_id=photo_id)
                description = '{} likes your photo.'.format(user.username)
                feed = Feed(feed_type=feed_type, user_to=photo.owner, description=description, photo=photo,
                            latest_user=user)
                feed.save()
            except ObjectDoesNotExist:
                pass
