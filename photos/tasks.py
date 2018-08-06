import json

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from follows.models import Follow
from tink_api.settings import r
from tink_api.celery import app
from .models import UploadedPhoto, PhotoStream, PhotoStreamPhoto

channel_name = 'recognition_results'
sub = r.pubsub()
sub.subscribe(channel_name)


@app.task
def create_stream():
    """
    listens to redis queue for recognition results
    """
    for item in sub.listen():
        if item['type'] == 'subscribe':
            print('Listening to channel {0}'.format(channel_name))
        elif item['type'] == 'message':
            info = json.loads(item['data'].decode())
            # get image id
            photo_id = info['photo_id']
            photo = UploadedPhoto.objects.get(pk=photo_id)
            photo.faces_found = info['num_faces']
            photo.process_status = 1
            photo.save()
            # get users in this image
            users = info['users_in_photo']

            # create photo stream for each user
            def yield_streams():
                for user in users:
                    user_id = user['user_id']
                    confidence = user['confidence']
                    if confidence >= 0.75:
                        # check for auto send
                        autosend = Follow.check_auto_send(photo.owner.pk, user_id)
                        # check if another unseen stream exists
                        # if it does, add image to this stream instead of creating new one
                        try:
                            stream = PhotoStream.objects.get(
                                to_user_id=user_id, from_user=photo.owner, seen=False)
                            # prevent image duplicates :)
                            try:
                                PhotoStreamPhoto.objects.get(photo=photo, stream=stream)
                            except ObjectDoesNotExist:
                                sp = PhotoStreamPhoto(stream=stream, photo=photo, send_photo=autosend)
                                # update stream time
                                stream.date_time = timezone.now()
                                stream.save(update_fields=['date_time'])
                                yield sp
                        except ObjectDoesNotExist:
                            ps = PhotoStream.objects.create(
                                from_user=photo.owner, to_user_id=user_id, send_all_photos=autosend)
                            sp = PhotoStreamPhoto(stream=ps, photo=photo, send_photo=autosend)
                            yield sp

            # insert photo streams to DB
            PhotoStreamPhoto.objects.bulk_create(list(yield_streams()))
