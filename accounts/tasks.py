from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from .models import Account



@shared_task
def send_welcome_mail(username, email):

    subject = f"Welcome to Fast-Shop"
    message = f"Hi {username}, Thanks for creating an account with us, hope you a good experement."

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]  # already a list, do not wrap again


    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=to_email  # correct
    )
    email.send()
    return True
