from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_lead_notification(inquiry):
    """Email a new inquiry to the company inbox. Never breaks the user request."""
    subject = f"New website inquiry from {inquiry.name}"
    body = render_to_string("emails/lead_notification.txt", {"inquiry": inquiry})
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [settings.LEADS_NOTIFY_EMAIL],
        fail_silently=True,
    )
