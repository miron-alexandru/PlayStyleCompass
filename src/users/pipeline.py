from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from playstyle_compass.models import UserPreferences 

from .tokens import account_activation_token


def send_email_confirmation(backend, user, response, *args, **kwargs):
    request = kwargs.get("request")
    is_new = kwargs.get("is_new")

    if is_new and not user.userprofile.email_confirmed:
        to_email = user.email
        mail_subject = str(_("Activate your user account."))
        message = render_to_string(
            "registration/activate_account.html",
            {
                "user": user.username,
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            },
        )
        email = EmailMessage(mail_subject, message, to=[to_email])
        if email.send():
            message = _(
                "Hello <b>%(user)s</b>, please go to your email <b>%(to_email)s</b> inbox and click on the received activation link to confirm your registration. <b>Note:</b> If you cannot find the email in your inbox, we recommend checking your spam folder."
            ) % {
                "user": user.username,
                "to_email": to_email,
            }
            messages.success(request, mark_safe(message))
        else:
            messages.error(
                request,
                _(
                    "Problem sending email to %(to_email)s, check if you typed it correctly."
                )
                % {"to_email": to_email},
            )

User = get_user_model()

def create_or_link_user(backend, uid, user=None, *args, **kwargs):
    """Ensure that only one account is linked to a social login."""
    email = kwargs.get('details', {}).get('email')
    
    if email:
        try:
            existing_user = User.objects.get(email=email)
            if existing_user and user != existing_user:
                # If there's already an account with this email, return the existing user
                return {'is_new': False, 'user': existing_user}
        except User.DoesNotExist:
            # No existing user found, proceed with new user creation
            pass
    return {'is_new': False, 'user': user}
