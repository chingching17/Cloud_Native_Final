# web_cn/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('myapp')

@shared_task
def send_notification(email, subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
