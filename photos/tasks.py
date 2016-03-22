from __future__ import absolute_import
import cv2

from celery import task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.conf.settings import BASE_DIR

from .models import UploadedPhoto

FACE_DETECTOR_PATH = '{}/photos/face_detection/cascades/haarcascade_frontalface_alt.xml/'.format(BASE_DIR)

@task
def detect_faces():
	pass
