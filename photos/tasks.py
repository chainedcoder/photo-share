import json

from celery import task

from tink_api.settings import r
from .models import UploadedPhoto, PhotoStream

channel_name = 'recognition_results'
sub = r.pubsub()
sub.subscribe(channel_name)


@task
def create_stream():
    """
    listens to redis queue for recognition results
    """
    for item in sub.listen():
        if item['type'] == 'subscribe':
            print 'Listening to channel {0}'.format(channel_name)
        elif item['type'] == 'message':
            info = json.loads(item['data'])
            # get image id
            photo_id = info['image_id']
            photo = UploadedPhoto.objects.get(pk=photo_id)
            photo.faces_found = info['num_faces']
            photo.process_status = 1
            photo.save()
            # get users in this image
            users = info['users_in_photo']
            streams = []
            # create photo stream for each user
            for user in users:
                ps = PhotoStream(from_user=photo.owner, to_user=user)
                streams.append(ps)
            # insert photo streams to DB
            PhotoStream.objects.bulk_create(streams)
