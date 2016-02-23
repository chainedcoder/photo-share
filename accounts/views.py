from django.shortcuts import render
from django.http import HttpResponse


def verify_email(request, email_verification_key):
    return HttpResponse('OK')
