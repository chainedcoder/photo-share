from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.urlresolvers import reverse
from django.shortcuts import render

from accounts.forms import BeginPasswordResetForm, MySetpasswordForm


def begin_password_reset(request):
    return password_reset(request, template_name='password_reset_begin.html',
                          password_reset_form=BeginPasswordResetForm,
                          email_template_name='notifications/begin_password_reset.html',
                          html_email_template_name='notifications/begin_password_reset.html',
                          subject_template_name='notifications/begin_password_reset_subject.txt',
                          post_reset_redirect=reverse('password-reset-initiated'))


def password_reset_initiated(request):
    return render(request, 'password_reset_initiated.html')


def reset_password(request, uidb64=None, token=None):
    return password_reset_confirm(request,
                                  template_name='password_reset_confirm.html',
                                  set_password_form=MySetpasswordForm,
                                  uidb64=uidb64, token=token,
                                  post_reset_redirect=reverse('password-reset-complete'))


def reset_password_complete(request):
    return render(request, 'password_reset_complete.html')
