from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings


def detectUser(user):
    """Determine the appropriate redirect URL based on the user's role."""
    if user.role == 1:
        return 'vendor_dashboard'
    elif user.role == 2:
        return 'customer_dashboard'
    elif user is None and user.is_superadmin:
        return '/admin'


def send_verification_mail(request, user, mail_subject, email_template):
    """Send a verification email to the user."""
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_mail = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_mail])
    mail.content_subtype = "html"
    try:
        mail.send()
    except Exception as e:
        print(f"Failed to send verification email: {e}")


def send_notification_mail(mail_subject, mail_template, context):
    """Send a notification email."""
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    to_email = context.get('to_email')
    if isinstance(to_email, str):
        to_email = [to_email]

    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    try:
        mail.send()
    except Exception as e:
        print(f"Failed to send notification email: {e}")

