from subprocess import call
from time import sleep

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.core.signals import request_finished

from .models import Feedback, Sources
from .views import auto_deploy


@receiver(post_save, sender=Feedback)
def send_new_feedback_email(sender, instance, **kwargs):
    try:
        if kwargs["created"]:
            send_mail('New feedback at {}'.format(settings.SHORT_SITE_NAME), \
                'The message {0}.\n\nName: {1}\n\nEmail: {2}'.format(instance.message, instance.name, instance.email), \
                settings.DEFAULT_FROM_EMAIL,
                settings.NOTIFICATIONS_EMAILS, \
                fail_silently=False)

            email = instance.email
            if email:
                send_mail('Thank you for your feedback for {}!'.format(settings.SHORT_SITE_NAME), \
                    "Thank you for your mesasge. If requested, we'll contact you shortly.\n\n", \
                    settings.DEFAULT_FROM_EMAIL,
                    [email], \
                    fail_silently=False)

    except:
        pass


@receiver(post_save, sender=Sources)
def send_new_source_email(sender, instance, **kwargs):
    try:
        if kwargs["created"]:
            send_mail('New source at {}'.format(settings.SHORT_SITE_NAME), \
                'New source registered, pelase visit to review.', \
                settings.DEFAULT_FROM_EMAIL,
                settings.NOTIFICATIONS_EMAILS, \
                fail_silently=False)

            email = instance.email
            if email:
                send_mail('Thank you for your addition in {}!'.format(settings.SHORT_SITE_NAME), \
                    "Thank you for your resource registration. We'll include it shortly if not yet and appropriate.\n\n", \
                    settings.DEFAULT_FROM_EMAIL,
                    [email], \
                    fail_silently=False)

    except:
        pass

@receiver(request_finished, sender=auto_deploy)
def restart_apps(sender, instance, **kwargs):
    sleep(300)
    call(["/bin/bash", "/home/restart_all_api.sh"])
    call(["/bin/bash", "/home/restart_all.sh"])
