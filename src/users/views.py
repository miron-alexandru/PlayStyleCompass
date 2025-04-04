"""Defines views."""

import time
import json
import ast
from datetime import timedelta
import asyncio
from typing import AsyncGenerator, AsyncIterable, AsyncIterator
from asgiref.sync import sync_to_async, async_to_sync
from channels.layers import get_channel_layer

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)

from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.views import LoginView

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.html import format_html, escape
from django.utils.encoding import (
    force_bytes,
    force_str,
)

from django.http import (
    JsonResponse,
    HttpResponse,
    Http404,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import default_token_generator

from playstyle_compass.models import UserPreferences, Review, Game, ListReview, GameList

from playstyle_compass.helper_functions.views_helpers import (
    paginate_matching_games,
    get_friend_list,
)

from .forms import (
    CustomRegistrationForm,
    DeleteAccountForm,
    EmailChangeForm,
    CustomPasswordChangeForm,
    ProfilePictureForm,
    ContactForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
    MessageForm,
    QuizForm,
    UserProfileForm,
    NotificationSettingsForm,
)

from .misc.helper_functions import (
    are_friends,
    check_quiz_time,
    QuizRecommendations,
    get_quiz_questions,
    save_quiz_responses,
    process_chat_notification,
    create_notification,
)

from .models import (
    UserProfile,
    FriendList,
    FriendRequest,
    Message,
    Notification,
    QuizUserResponse,
    ChatMessage,
    Follow,
    GlobalChatMessage,
)
from .tokens import account_activation_token, account_deletion_token


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    This view allows users to update their profile name and restricts the frequency of updates.

    Attributes:
    - model: The model to be updated (UserProfile).
    - template_name: The template used for rendering the update form.
    - form_class: The form class used for the update.
    - success_url: The URL to redirect to after a successful update.
    """

    model = UserProfile
    template_name = "account_actions/profile_name_update.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("playstyle_compass:index")

    def get_object(self, queryset=None):
        """Get the UserProfile object associated with the current user."""
        return self.request.user.userprofile

    def dispatch(self, request, *args, **kwargs):
        """Check the time since the last profile name update and restrict frequent updates."""
        if last_update_time := self.request.user.userprofile.name_last_update_time:
            one_hour_ago = timezone.now() - timedelta(hours=1)
            if last_update_time > one_hour_ago:
                time_remaining = last_update_time - one_hour_ago
                minutes_remaining = int(time_remaining.total_seconds() // 60)
                seconds_remaining = int(time_remaining.total_seconds() % 60)
                error_message = _(
                    "You can only update your profile name once per hour. Please try again in {} minutes and {} seconds."
                ).format(minutes_remaining, seconds_remaining)
                messages.error(self.request, error_message)
                return redirect(
                    self.request.META.get("HTTP_REFERER", "playstyle_compass:index")
                )
        return super().dispatch(request, *args, **kwargs)

    def update_user_reviews(self, new_profile_name):
        """Update the profile name in user reviews after a profile name change."""
        user_reviews = Review.objects.filter(user=self.request.user)

        for review in user_reviews:
            review.reviewers = new_profile_name
            review.save()

    def form_valid(self, form):
        """Save the form data and update the user profile and associated reviews."""
        new_profile_name = form.cleaned_data["profile_name"]

        self.object = form.save()

        # Update the user profile's last update time
        self.object.name_last_update_time = timezone.now()
        self.object.save()

        self.update_user_reviews(new_profile_name)

        messages.success(
            self.request, _("Your profile name has been successfully changed!")
        )

        return super().form_valid(form)


class CustomLoginView(LoginView):
    """Custom user login view."""

    authentication_form = CustomAuthenticationForm
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("playstyle_compass:index")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        remember_me = form.cleaned_data.get("remember_me")

        if remember_me:
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)

        return response


def custom_logout(request):
    """Custom logout view."""
    logout(request)

    return render(request, "registration/logged_out.html")


@login_required
def activate(request, uidb64, token):
    """Email activation view."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except ObjectDoesNotExist:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.userprofile.email_confirmed = True
        user.userprofile.save()
        user.save()

        messages.success(request, _("Thank you for your email confirmation!"))
        return redirect("playstyle_compass:index")
    else:
        messages.error(request, _("Activation link is invalid!"))

    return redirect("playstyle_compass:index")


@require_POST
@login_required
def activate_email(request, user, to_email):
    """Send activation email to users."""
    if not user.userprofile.email_confirmed:
        mail_subject = _("Activate your user account.")
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
            message = format_html(
                "Hello <b>{}</b>, please go to your email <b>{}</b> inbox and click on the received activation link to confirm your registration. Note: If you cannot find the email in your inbox, we recommend checking your spam folder.",
                user,
                to_email,
            )
            messages.success(request, message)
        else:
            messages.error(
                request,
                _(
                    "Problem sending email to %(to_email)s, check if you typed it correctly."
                )
                % {"to_email": to_email},
            )
    else:
        messages.error(request, _("Email address already confirmed!"))


@require_POST
@login_required
def send_deletion_email(request):
    """Send account deletion confirmation email."""
    user = request.user
    if not user.userprofile.email_confirmed:
        messages.error(request, _("Email address not confirmed!"))
        return redirect("playstyle_compass:index")

    mail_subject = _("Confirm your account deletion.")
    message = render_to_string(
        "registration/delete_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_deletion_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = "html"
    if email.send():
        message = format_html(
            "Hello <strong>{}</strong> please go to your email <strong>{}</strong> inbox and click on the received link to confirm your account deletion. Note: If you cannot find the email in your inbox, we recommend checking your spam folder.",
            user.username,
            user.email,
        )

        messages.success(request, message)
    else:
        messages.error(
            request,
            _("Problem sending email to %(to_email)s, check if you typed it correctly.")
            % {"to_email": user.email},
        )
    return redirect("playstyle_compass:index")


@require_POST
@login_required
def resend_activation_link(request):
    """Resend email activation link to the user."""
    email = request.user.email
    user = get_object_or_404(User, email=email)
    activate_email(request, user, email)

    return JsonResponse({})


def register(request):
    """View function for user registration."""
    if request.user.is_authenticated:
        return redirect("playstyle_compass:index")

    if request.method == "POST":
        form = CustomRegistrationForm(data=request.POST)

        if form.is_valid():
            return register_user(form, request)
    else:
        form = CustomRegistrationForm()

    context = {"form": form, "page_title": _("Register :: PlayStyle Compass")}

    return render(request, "registration/register.html", context)


def register_user(form, request):
    """Function to successfully register a user."""
    new_user = form.save(commit=False)
    new_user.set_password(form.cleaned_data["password1"])
    new_user._profile_created = True
    new_user.save()

    user_profile = UserProfile(
        user=new_user,
        profile_name=form.cleaned_data["profile_name"],
    )

    user_profile.profile_picture = (
        "profile_pictures/default_pfp/default_profile_picture.png"
    )
    user_profile.timezone = request.headers.get("timezone")

    user_profile.save()
    new_user.save()

    login(request, new_user, backend="django.contrib.auth.backends.ModelBackend")
    activate_email(request, new_user, form.cleaned_data.get("email"))

    return redirect("playstyle_compass:index")


@login_required
def delete_account(request):
    """View for deleting a user's account."""
    if request.method == "POST":
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            if "delete_with_password" in request.POST:
                # Delete account with password
                password = form.cleaned_data["password"]
                if request.user.check_password(password):
                    request.user.delete()
                    messages.success(
                        request, _("Your account has been successfully deleted!")
                    )
                    return redirect("playstyle_compass:index")
                else:
                    form.add_error(
                        "password", _("Incorrect password. Please try again.")
                    )

            elif "delete_with_email" in request.POST:
                # Send email for account deletion confirmation
                if request.user.userprofile.email_confirmed:
                    mail_subject = _("Confirm your account deletion.")
                    message = render_to_string(
                        "registration/delete_account.html",
                        {
                            "user": request.user,
                            "domain": get_current_site(request).domain,
                            "uid": urlsafe_base64_encode(force_bytes(request.user.pk)),
                            "token": account_deletion_token.make_token(request.user),
                            "protocol": "https" if request.is_secure() else "http",
                        },
                    )
                    email = EmailMessage(mail_subject, message, to=[request.user.email])
                    if email.send():
                        messages.success(
                            request,
                            _(
                                "A confirmation email has been sent to your address. Please follow the instructions to complete the deletion process."
                            ),
                        )
                    else:
                        messages.error(
                            request,
                            _(
                                "Problem sending email to %(to_email)s, please check if it is correct."
                            )
                            % {"to_email": request.user.email},
                        )
                else:
                    messages.error(
                        request,
                        _(
                            "Please confirm your email address before attempting to delete your account."
                        ),
                    )
    else:
        form = DeleteAccountForm()

    context = {"form": form, "page_title": _("Delete Account :: PlayStyle Compass")}
    return render(request, "account_actions/delete_account.html", context)


@login_required
def confirm_deletion(request, uidb64, token):
    """Confirm the account deletion request via a confirmation link."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_deletion_token.check_token(user, token):
        user.delete()
        messages.success(request, _("Your account has been deleted successfully."))
        return redirect("playstyle_compass:index")
    else:
        messages.error(request, _("The confirmation link is invalid or has expired."))
        return redirect("playstyle_compass:index")


@login_required
def change_email(request):
    """This view allows authenticated users to request a change of their email address
    and sends a confirmation email.
    """

    if request.method == "POST":
        form = EmailChangeForm(request.POST, user=request.user)

        if form.is_valid():
            # Get the new email from the form's cleaned data
            new_email = form.cleaned_data["new_email"]

            # Generate a token for email verification
            token = default_token_generator.make_token(request.user)

            # Encode the user ID for inclusion in the verification URL
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))

            # Store the new email and token in the session for verification
            request.session["email_change_temp"] = new_email
            request.session["email_change_token"] = token

            # Build the confirmation URL
            confirm_url = request.build_absolute_uri(
                reverse(
                    "users:confirm_email_change", kwargs={"uidb64": uid, "token": token}
                )
            )

            # Email subject, sender, and message
            subject = _("Confirm Email Change")
            from_email = settings.DEFAULT_FROM_EMAIL
            message = render_to_string(
                "account_actions/confirm_email_change.txt",
                {"confirm_url": confirm_url, "new_email": new_email},
            )

            # Send the confirmation email
            send_mail(subject, message, from_email, [request.user.email])

            # Redirect to a success page after initiating the email change
            return redirect("users:change_email_done")
    else:
        form = EmailChangeForm(
            user=request.user, initial={"current_email": request.user.email}
        )

    context = {"form": form, "page_title": _("Change Email :: PlayStyle Compass")}

    return render(request, "account_actions/change_email.html", context)


def confirm_email_change(request, uidb64, token):
    """View for email change confirmation."""
    if (
        "email_change_token" in request.session
        and request.session["email_change_token"] == token
    ):
        user = request.user

        user.email = request.session["email_change_temp"]
        user.save()

        del request.session["email_change_temp"]
        del request.session["email_change_token"]

        return redirect("users:change_email_success")

    return HttpResponse(_("Invalid token for email change."))


@login_required
def change_email_success(request):
    """View for email change success."""
    new_email = request.user.email
    messages.success(request, _("Email Address successfully changed!"))
    context = {
        "page_title": _("Email Change Success :: PlayStyle Compass"),
        "response": _(
            "You have successfully changed your email address, go to the homepage by clicking the button below."
        ),
        "additional_message": new_email,
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def change_email_done(request):
    """View for email change confirmation."""
    messages.success(request, _("Confirmation email successfully sent!"))
    context = {
        "page_title": _("Email Change Done :: PlayStyle Compass"),
        "response": _(
            "An email confirmation has been sent to your current email address. Please check your inbox and click the link provided to confirm the email change."
        ),
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def change_password(request):
    """This view allows authenticated users to change their passwords."""

    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            # Get the new passwords from the form's cleaned data
            password1 = form.cleaned_data["new_password1"]
            password2 = form.cleaned_data["new_password2"]

            # Check if the new passwords match
            if password1 == password2:
                # Check if the new password is different from the old password
                if not request.user.check_password(password1):
                    # Set and save the new password for the user
                    request.user.set_password(password1)
                    request.user.save()

                    # Update the session auth hash to prevent log out
                    update_session_auth_hash(request, request.user)

                    # Redirect to a success page after changing the password
                    return redirect("users:change_password_done")
                else:
                    messages.error(
                        request,
                        _("New password must be different from the old password!"),
                    )
            else:
                form.add_error("new_password2", _("New passwords must match."))
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        "form": form,
        "page_title": _("Change Password :: PlayStyle Compass"),
    }

    return render(request, "account_actions/password_change_form.html", context)


@login_required
def change_password_done(request):
    """View for password change confirmation."""
    messages.success(request, _("Password Changed Successfully!"))
    context = {
        "page_title": _("Password Change Done :: PlayStyle Compass"),
        "response": _(
            "Your password has been successfully changed!<br><br>"
            "To return to the homepage, please click the button below."
        ),
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def update_profile_picture(request):
    """View for profile image update."""
    if request.method == "POST":
        form = ProfilePictureForm(
            request.POST, request.FILES, instance=request.user.userprofile
        )

        if form.is_valid():
            form.save()
            return redirect("users:profile_picture")

    else:
        form = ProfilePictureForm(instance=request.user.userprofile)

    context = {
        "form": form,
        "page_title": _("Change Profile Picture :: PlayStyle Compass"),
    }

    return render(request, "account_actions/update_profile_picture.html", context)


def contact(request):
    """Contact view."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            return send_contact_form(form)
    else:
        form = ContactForm()

    context = {"form": form, "page_title": _("Contact Us :: PlayStyle Compass")}

    return render(request, "general/contact.html", context)


def send_contact_form(form):
    """Function to send a contact form."""
    contact_message = form.save()
    subject = "New Conctat Us Submission"

    message = f"""
                Name: {contact_message.name}
                Email: {contact_message.email}
                Subject: {contact_message.subject}
                Message: {contact_message.message}
                Time: {contact_message.formatted_timestamp()}
            """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.EMAIL_USER_CONTACT]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return redirect("users:contact_success")


def contact_success(request):
    """Contact confirmation view."""
    messages.success(request, _("Your message has been successfully submitted!"))

    context = {
        "page_title": _("Contact Us Done :: PlayStyle Compass"),
        "response": _(
            "Thank you for contacting us! Our team will review it within 48 hours and get back to you as soon as possible. \
    Go to the homepage by clicking the button below."
        ),
    }

    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def friends_list_view(request, *args, **kwargs):
    """View to display the friends list."""
    viewer = request.user
    context = {}

    if not viewer.is_authenticated:
        return HttpResponse(_("You must be authenticated to view the friends list."))

    user_id = kwargs.get("user_id")
    this_user = get_object_or_404(User, pk=user_id)

    if viewer != this_user:
        return HttpResponse(_("You cannot view the friends list of another user."))

    friend_list, created = FriendList.objects.get_or_create(user=this_user)
    auth_user_friend_list = get_object_or_404(FriendList, user=request.user)

    friends = [(friend, auth_user_friend_list) for friend in friend_list.friends.all()]

    context = {
        "page_title": _("Friends List :: PlayStyle Compass"),
        "this_user": this_user,
        "friends": friends,
    }

    return render(request, "user_related/friends_list.html", context)


@login_required
def friend_requests_view(request, *args, **kwargs):
    """View to see all friend requests."""
    user = request.user

    if not user.is_authenticated:
        return redirect("playstyle_compass:index")

    user_id = kwargs.get("user_id")
    account = get_object_or_404(User, pk=user_id)

    if account != user:
        return HttpResponse(_("You can't view the friend requests of another user."))

    friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
    user_sent_friend_requests = FriendRequest.objects.filter(
        sender=user, is_active=True
    )

    context = {
        "page_title": _("Friend Requests :: PlayStyle Compass"),
        "friend_requests": friend_requests,
        "user_sent_friend_requests": user_sent_friend_requests,
    }

    return render(request, "user_related/friend_requests.html", context)


@login_required
def send_friend_request(request, *args, **kwargs):
    """This view allows users to send friend requests to other users."""
    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("user_id", "invalid_user")

        if user_id and user_id != "invalid_user" and user_id.isdigit():
            # Get the receiver user object based on the provided user ID
            receiver_queryset = User.objects.filter(pk=user_id)

            if receiver_queryset.exists():
                # Get the first user from the queryset
                receiver = receiver_queryset.first()

                # Check if the users are already friends
                if are_friends(user, receiver):
                    result["message"] = _(
                        "<strong>%(profile_name)s</strong> is already in your friends list."
                    ) % {"profile_name": receiver.userprofile.profile_name}

                # Check if the user is trying to send a request to themselves
                elif user == receiver:
                    result["message"] = _(
                        "You cannot send a friend request to <strong>yourself.</strong>"
                    )
                else:
                    # Check if there are existing active friend requests from the current user to the receiver
                    friend_requests = FriendRequest.objects.filter(
                        sender=user, receiver=receiver, is_active=True
                    )

                    # Check if the user has already sent a friend request to the receiver
                    if friend_requests.exists():
                        result["message"] = _(
                            "You already sent a friend request to this user."
                        )
                    else:
                        try:
                            # Attempt to retrieve an existing friend request (may not exist)
                            friend_request = FriendRequest.objects.get(
                                sender=user, receiver=receiver
                            )
                            friend_request.is_active = True
                            friend_request.save()
                        except FriendRequest.DoesNotExist:
                            # Create a new friend request if it doesn't exist
                            friend_request = FriendRequest(
                                sender=user, receiver=receiver, is_active=True
                            )
                            friend_request.save()

                        result["message"] = _("Friend request sent.")

                        user_in_notification = user.userprofile.profile_name
                        profile_url = reverse(
                            "users:view_profile", args=[user_in_notification]
                        )
                        navigation_url = reverse(
                            "users:friend_requests", args=[receiver.id]
                        )

                        message = (
                            f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a> '
                            "just sent you a friend request!<br>"
                            f'<a class="notification-link" title="Navigate" href="{navigation_url}">View friend requests</a>'
                        )

                        create_notification(
                            receiver,
                            message=message,
                            notification_type="friend_request",
                            profile_url=profile_url,
                            user_in_notification=user_in_notification,
                            navigation_url=navigation_url,
                        )

            else:
                result["message"] = _(
                    "The user does not exist or has deleted their account."
                )
        else:
            result["message"] = _(
                "The user does not exist or has deleted their account."
            )
    else:
        result["message"] = _("You must be logged in to send a friend request.")

    return HttpResponse(json.dumps(result), content_type="application/json")


@require_POST
@login_required
def accept_friend_request(request, *args, **kwargs):
    """View to accept a friend request."""
    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        if friend_request_id := kwargs.get("friend_request_id"):
            friend_request = get_object_or_404(FriendRequest, pk=friend_request_id)

            if friend_request.receiver == user:
                try:
                    friend_request.accept()
                    friend_request.delete()
                    result["message"] = _("Friend request accepted.")
                    messages.success(
                        request,
                        format_html(
                            "You are now friends with <strong>{}</strong>.",
                            friend_request.sender.userprofile.profile_name,
                        ),
                    )

                    user_in_notification = (
                        friend_request.receiver.userprofile.profile_name
                    )
                    profile_url = reverse(
                        "users:view_profile", args=[user_in_notification]
                    )

                    message = (
                        f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a> '
                        "accepted your friend request!"
                    )

                    create_notification(
                        friend_request.sender,
                        message=message,
                        notification_type="friend_request",
                        profile_url=profile_url,
                        user_in_notification=user_in_notification,
                        friend_request_acc=True,
                    )

                except Exception as e:
                    result["message"] = str(e)
            else:
                result["message"] = _("That is not your request to accept.")
        else:
            result["message"] = _("Unable to accept that friend request.")
    else:
        result["message"] = _("You must be authenticated to accept a friend request.")

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def remove_friend(request):
    """View to remove a friend."""
    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        if receiver_user_id := request.POST.get("receiver_user_id"):
            friend_to_remove = get_object_or_404(User, pk=receiver_user_id)
            friend_list = get_object_or_404(FriendList, user=user)

            try:
                friend_list.unfriend(friend_to_remove)
                result["message"] = _("Successfully removed that friend.")
                messages.success(
                    request,
                    format_html(
                        "You are no longer friends with <strong>{}</strong>.",
                        friend_to_remove.userprofile.profile_name,
                    ),
                )

            except Exception as e:
                result["message"] = str(e)
        else:
            result["message"] = _("There was an error. Unable to remove that friend.")
    else:
        result["message"] = _("You must be authenticated to remove a friend.")

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def decline_friend_request(request, *args, **kwargs):
    """View to decline a friend request."""
    user = request.user
    result = {}

    if request.method == "GET" and user.is_authenticated:
        if friend_request_id := kwargs.get("friend_request_id"):
            friend_request = get_object_or_404(FriendRequest, pk=friend_request_id)

            if friend_request.receiver == user:
                try:
                    friend_request.decline()
                    result["message"] = _("Friend request declined.")
                    messages.success(
                        request,
                        format_html(
                            "You refused to be friends with <strong>{}</strong>.",
                            friend_request.sender.userprofile.profile_name,
                        ),
                    )

                    user_in_notification = (
                        friend_request.receiver.userprofile.profile_name
                    )
                    profile_url = reverse(
                        "users:view_profile", args=[user_in_notification]
                    )

                    message = (
                        f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a> '
                        "declined your friend request!"
                    )

                    create_notification(
                        friend_request.sender,
                        message=message,
                        notification_type="friend_request",
                        profile_url=profile_url,
                        user_in_notification=user_in_notification,
                        friend_request_decline=True,
                    )

                except Exception as e:
                    result["message"] = str(e)
            else:
                result["message"] = _("That is not your friend request to decline.")
        else:
            result["message"] = _("Unable to decline that friend request.")
    else:
        result["message"] = _("You must be authenticated to decline a friend request.")

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def cancel_friend_request(request):
    """View to cancel a friend request."""

    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        # Get the receiver's user ID from the POST data and then the receiver
        if receiver_user_id := request.POST.get("receiver_user_id"):
            receiver = get_object_or_404(User, pk=receiver_user_id)

            try:
                # Attempt to retrieve active friend requests from the current user to the receiver
                friend_requests = FriendRequest.objects.filter(
                    sender=user, receiver=receiver, is_active=True
                )
            except FriendRequest.DoesNotExist:
                # Handle the case where no friend request exists
                result["message"] = _(
                    "Nothing to cancel. Friend request does not exist."
                )
            else:
                # Cancel each friend request
                for friend_request in friend_requests:
                    friend_request.cancel()

                result["message"] = _("Friend request canceled.")

                messages.success(
                    request,
                    format_html(
                        "You canceled your friend request for <strong>{}</strong>.",
                        receiver.userprofile.profile_name,
                    ),
                )

        else:
            result["message"] = _("Unable to cancel that friend request.")
    else:
        result["message"] = _("You must be authenticated to cancel a friend request.")

    return HttpResponse(json.dumps(result), content_type="application/json")


def view_profile(request, profile_name):
    """View used to view the profile of users."""
    context = {"page_title": _("User Profile :: PlayStyle Compass")}

    try:
        user_profile = get_object_or_404(UserProfile, profile_name=profile_name)
        user = user_profile.user

        user_stats = get_user_stats(user)

        request_user = request.user
        profile_to_view = user_profile.user

        is_blocked = (
            profile_to_view in request_user.userprofile.blocked_users.all()
            if request.user.is_authenticated
            else None
        )
        is_friend = get_friend_status(request_user, profile_to_view)
        is_following = (
            Follow.objects.filter(follower=request.user, followed=user).exists()
            if request.user.is_authenticated
            else None
        )

        context.update(
            {
                "user_profile": user_profile,
                "is_friend": is_friend,
                "user_id": user.id,
                "user_preferences": user_stats["user_preferences"],
                "user_reviews_count": user_stats["user_reviews_count"],
                "review_likes_count": user_stats["review_likes_count"],
                "follower_count": user_stats["follower_count"],
                "following_count": user_stats["following_count"],
                "game_list_count": user_stats["game_list_count"],
                "game_list_reviews_count": user_stats["game_list_reviews_count"],
                "show_in_queue": user_stats["user_preferences"].show_in_queue,
                "show_reviews": user_stats["user_preferences"].show_reviews,
                "show_favorites": user_stats["user_preferences"].show_favorites,
                "is_blocked": is_blocked,
                "is_following": is_following,
            }
        )

    except Http404:
        return JsonResponse({"exists": False})

    return render(request, "user_related/user_profile.html", context)


@login_required
@require_POST
def toggle_show_stat(request):
    """Toggle the show/hide of user stats on their profile."""
    stat_name = request.POST.get("statName")
    user_id = request.POST.get("userId")

    user_preferences = get_object_or_404(UserPreferences, user_id=user_id)

    attribute_name = f"show_{stat_name}"
    show_value = getattr(user_preferences, attribute_name, False)
    show_value = not show_value

    setattr(user_preferences, attribute_name, show_value)
    user_preferences.save()

    return JsonResponse({"show": show_value})


def get_friend_status(request_user, profile_to_view):
    """Determine the friend status."""
    if request_user.is_authenticated:
        if request_user == profile_to_view:
            return _("You")
        elif are_friends(request_user, profile_to_view):
            return _("Friend")
        else:
            return _("Stranger")
    else:
        return None


def get_user_stats(user):
    """Get user stats."""
    user_preferences = get_object_or_404(UserPreferences, user=user)

    reviews = Review.objects.filter(user=user)
    user_reviews_count = reviews.count()

    review_likes_count = 0
    for review in reviews:
        review_likes_count += review.likes

    follower_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    game_list_count = GameList.objects.filter(owner=user).count()
    game_list_reviews_count = ListReview.objects.filter(user=user).count()

    return {
        "user_preferences": user_preferences,
        "user_reviews_count": user_reviews_count,
        "review_likes_count": review_likes_count,
        "follower_count": follower_count,
        "following_count": following_count,
        "game_list_count": game_list_count,
        "game_list_reviews_count": game_list_reviews_count,
    }


@login_required
def send_message(request, user_id):
    """View used to send messages between users."""
    message_sender = request.user
    message_receiver = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        if message_sender in message_receiver.userprofile.blocked_users.all():
            profile_name = message_receiver.userprofile.profile_name
            messages.error(request, f"{profile_name} is no longer available.")
            return redirect(request.META.get("HTTP_REFERER", "users:inbox"))

        if message_receiver in message_sender.userprofile.blocked_users.all():
            profile_name = message_receiver.userprofile.profile_name
            messages.error(request, f"{profile_name} is in your block list.")
            return redirect(request.META.get("HTTP_REFERER", "users:inbox"))

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.instance
            message.sender = message_sender
            message.receiver = message_receiver
            message.save()
            messages.success(request, _("Message sent successfully!"))

            profile_url = reverse(
                "users:view_profile", args=[message_sender.userprofile.profile_name]
            )
            navigation_url = reverse("users:inbox")
            user_in_notification = message_sender.userprofile.profile_name

            notification_message = (
                f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a> '
                "just sent you a message!<br>"
                f'<a class="notification-link" title="Navigate" href="{navigation_url}">View inbox</a>'
            )

            create_notification(
                message_receiver,
                message=notification_message,
                notification_type="message",
                profile_url=profile_url,
                user_in_notification=user_in_notification,
                navigation_url=navigation_url,
            )

            return redirect(request.META.get("HTTP_REFERER", "users:inbox"))
    else:
        form = MessageForm()

    context = {
        "page_title": _("Send message :: PlayStyle Compass"),
        "form": form,
        "receiver": message_receiver.userprofile.profile_name,
    }

    return render(request, "messaging/send_message.html", context)


@login_required
def inbox(request):
    """View used to display messages received and sent by the user."""
    sort_order = request.GET.get("sort_order", "asc")
    active_category = request.GET.get("category", "received")

    if active_category == "received":
        user_messages = Message.objects.filter(
            receiver=request.user, is_deleted_by_receiver=False
        )
    elif active_category == "sent":
        user_messages = Message.objects.filter(
            sender=request.user, is_deleted_by_sender=False
        )
    else:
        user_messages = []

    # Sort the messages based on the selected order
    if sort_order == "asc":
        user_messages = user_messages.order_by("timestamp")
    else:
        user_messages = user_messages.order_by("-timestamp")

    context = {
        "page_title": _("Inbox :: PlayStyle Compass"),
        "user_messages": user_messages,
        "selected_sort_order": sort_order,
        "category": active_category,
    }

    return render(request, "messaging/inbox.html", context)


@login_required
def delete_messages(request):
    """View used to delete selected shared games."""

    if request.method == "POST":
        # Get the list of received and sent messages
        received_messages_to_delete = request.POST.getlist("received_messages[]")
        sent_messages_to_delete = request.POST.getlist("sent_messages[]")

        # Update the 'is_deleted_by_receiver' and 'is_deleted_by_sender'
        # fields for both received and sent messages
        Message.objects.filter(
            id__in=received_messages_to_delete, receiver=request.user
        ).update(is_deleted_by_receiver=True)

        Message.objects.filter(
            id__in=sent_messages_to_delete, sender=request.user
        ).update(is_deleted_by_sender=True)

        # Delete messages that meet certain conditions:
        # 1. Both sender and receiver marked as deleted
        # 2. Marked as deleted by receiver and sender is null
        # 3. Marked as deleted by sender and receiver is null
        Message.objects.filter(
            Q(is_deleted_by_receiver=True, is_deleted_by_sender=True)
            | Q(is_deleted_by_receiver=True, sender__isnull=True)
            | Q(is_deleted_by_sender=True, receiver__isnull=True)
        ).delete()

        category = request.GET.get("category", "")
        sort_order = request.GET.get("sort_order", "")
        inbox_url = (
            reverse("users:inbox") + f"?category={category}&sort_order={sort_order}"
        )

    return redirect(inbox_url)


@require_POST
@login_required
def mark_notification_as_read(request, notification_id=None):
    """View to mark notification(s) as read."""
    notifications = Notification.objects.filter(user=request.user)

    if notification_id is not None:
        # Mark a specific notification as read
        notification = notifications.get(pk=notification_id)
        notification.is_read = True
        notification.save()
    else:
        # Mark all notifications as read
        notifications.update(is_read=True)

    return JsonResponse({"status": "success"})


@require_POST
@login_required
def delete_notification(request, notification_id=None):
    """View to delete notification(s)."""
    notifications = Notification.objects.filter(user=request.user)

    if notification_id is not None:
        # Delete a specific notification
        notification = notifications.get(pk=notification_id)
        notification.delete()
    else:
        # Delete all notifications
        notifications.delete()

    return JsonResponse({"status": "success"})


def check_authentication(request):
    """Check if an user is authenticated."""
    if request.user.is_authenticated:
        return JsonResponse({"authenticated": True})
    else:
        return JsonResponse({"authenticated": False})


@login_required
def quiz_view(request):
    """View used to display quiz questions and processes submitted answers."""
    user = request.user

    time_remaining = check_quiz_time(user)
    if time_remaining is not None:
        error_message = _(
            "You can only take the quiz once per day. Please try again in {}"
        ).format(time_remaining)
        messages.error(request, error_message)
        return redirect(request.META.get("HTTP_REFERER", "playstyle_compass:index"))

    cache_key = f"quiz_questions_{user.id}"

    if not user.userprofile.quiz_taken and cache_key in cache:
        questions = cache.get(cache_key)
    else:
        questions = get_quiz_questions(user, cache_key)

    if request.method == "POST":
        form = QuizForm(request.POST, questions=questions)

        if form.is_valid():
            save_quiz_responses(user, questions, form)
            user.userprofile.quiz_taken_date = timezone.now()
            user.userprofile.quiz_taken = True
            user.userprofile.save()

            user_responses = QuizUserResponse.objects.filter(user=user).order_by(
                "-updated_at"
            )[:10]

            game_recommendations = QuizRecommendations(user_responses, user)
            game_recommendations.get_recommendations()

            messages.success(
                request,
                format_html(
                    _(
                        "Thank you for completing the Preference Quiz! Your responses will help us provide personalized game recommendations tailored just for you. Click <a href='{0}'>here</a> to view your Quiz Recommendations."
                    ).format(reverse("users:quiz_recommendations"))
                ),
            )
            return redirect("playstyle_compass:index")
    else:
        form = QuizForm(questions=questions)

    context = {
        "page_title": _("Preference Quiz :: PlayStyle Compass"),
        "questions": questions,
        "form": form,
    }

    return render(request, "general/quiz_template.html", context)


@login_required
def quiz_recommendations(request):
    """View used to display games based on the preference quiz taken by the user."""
    user = request.user
    user_preferences = get_object_or_404(UserPreferences, user=user)
    user_friends = get_friend_list(user) if user else []

    time_remaining = check_quiz_time(user)

    recommended_game_guids_str = user_preferences.quiz_recommendations
    recommended_game_guids = ast.literal_eval(recommended_game_guids_str)
    recommended_games = Game.objects.filter(guid__in=recommended_game_guids)

    recommended_games = paginate_matching_games(request, recommended_games)

    context = {
        "page_title": _("Quiz Recommendations :: PlayStyle Compass"),
        "games": recommended_games,
        "user_preferences": user_preferences,
        "user_friends": user_friends,
        "pagination": True,
        "page_info": True,
        "time_remaining": time_remaining,
    }

    return render(request, "general/quiz_recommendations.html", context)


@login_required
def profile_details(request):
    """View used to edit user profile information."""
    user_profile = request.user.userprofile
    profile_name = request.user.userprofile.profile_name

    if request.method == "POST":
        if "reset_profile" in request.POST:
            user_profile.bio = ""
            user_profile.gaming_alias = ""
            user_profile.current_game = ""
            user_profile.last_finished_game = ""
            user_profile.favorite_game = ""
            user_profile.favorite_franchise = ""
            user_profile.favorite_character = ""
            user_profile.favorite_soundtrack = ""
            user_profile.gaming_genres = ""
            user_profile.favorite_game_modes = ""
            user_profile.gaming_commitment = ""
            user_profile.main_gaming_platform = ""
            user_profile.gaming_setup = ""
            user_profile.streaming_preferences = ""
            user_profile.social_media = ""

            user_profile.save()
            return redirect("users:view_profile", profile_name=profile_name)

        else:
            form = UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                return redirect("users:view_profile", profile_name=profile_name)

    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        "page_title": _("Profile Details :: PlayStyle Compass"),
        "form": form,
        "user_profile": user_profile,
    }

    return render(request, "user_related/profile_details.html", context)


@login_required
def chat(request, recipient_id: int):
    """View used to open the chat with a certain user."""
    recipient = get_object_or_404(User, id=recipient_id)

    request.session["user_id"] = request.user.id
    request.session["recipient_id"] = recipient.id

    context = {
        "page_title": _("Chat :: PlayStyle Compass"),
        "recipient": recipient,
    }

    return render(request, "messaging/chat.html", context)


@login_required
def create_message(request):
    """View to create/send a chat message to a user."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    content = request.POST.get("content")
    file_url = None
    file_size = None
    user_id = request.session.get("user_id")
    recipient_id = request.session.get("recipient_id")

    if not user_id or not recipient_id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    sender = get_object_or_404(User, id=user_id)
    recipient = get_object_or_404(User, id=recipient_id)

    if sender in recipient.userprofile.blocked_users.all():
        profile_name = recipient.userprofile.profile_name
        return JsonResponse(
            {"error": f"{profile_name} is no longer available."}, status=403
        )

    if recipient in sender.userprofile.blocked_users.all():
        profile_name = recipient.userprofile.profile_name
        return JsonResponse(
            {"error": f"{profile_name} is in your block list."}, status=403
        )

    if not content and not "file" in request.FILES:
        return JsonResponse({"error": "You must write something"}, status=400)

    if "file" in request.FILES:
        file = request.FILES["file"]
        file_size = file.size

        if file.size > 25 * 1024 * 1024:
            return JsonResponse(
                {"error": "File size exceeds the limit (Max: 25 MB)."}, status=400
            )

        file_name = default_storage.save(
            f"chat_files/{file.name}", ContentFile(file.read())
        )
        file_url = default_storage.url(file_name)

    # Rate limiting check -> max 20 messages in 20 seconds
    cache_key = f"message_count_{user_id}"
    current_time = time.time()

    message_info = cache.get(cache_key, {"count": 0, "timestamps": []})
    message_info["timestamps"] = [
        ts for ts in message_info["timestamps"] if current_time - ts < 20
    ]

    if len(message_info["timestamps"]) >= 20:
        return JsonResponse(
            {"error": "You are sending messages too quickly. Please slow down."},
            status=429,
        )

    message_info["timestamps"].append(current_time)
    message_info["count"] = len(message_info["timestamps"])

    cache.set(cache_key, message_info, timeout=20)

    message = ChatMessage.objects.create(
        sender=sender,
        recipient=recipient,
        content=content,
        file=file_url if file_url else None,
        file_size=file_size if file_size else None,
    )

    room_group_name = (
        f"private_chat_{min(sender.id, recipient.id)}_{max(sender.id, recipient.id)}"
    )
    is_pinned = sender in message.pinned_by.all()

    message_data = {
        "type": "private_chat_message",
        "message": content,
        "sender_id": sender.id,
        "recipient_id": recipient.id,
        "file": file_url if file_url else None,
        "file_size": file_size if file_size else None,
        "profile_picture_url": sender.userprofile.profile_picture.url,
        "is_pinned": is_pinned,
        "edited": message.edited,
        "id": message.id,
    }
    channel_layer = get_channel_layer()
    channel_layer.group_send(room_group_name, message_data)

    process_chat_notification(sender, recipient)

    response_data = {
        "status": "Message created",
        "id": message.id,
        "file": file_url if file_url else None,
        "file_size": file_size if file_size else None,
        "edited": message.edited,
        "is_pinned": is_pinned,
    }

    return JsonResponse(response_data, status=201)


@login_required
def edit_message(request, message_id):
    """View to edit a chat message."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    new_content = request.POST.get("content")
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    sender = get_object_or_404(User, id=user_id)
    message = get_object_or_404(ChatMessage, id=message_id, sender=sender)

    edit_time_limit = timedelta(minutes=2)
    if timezone.now() > message.created_at + edit_time_limit:
        return JsonResponse(
            {"error": "Message editing time limit exceeded"}, status=403
        )

    if not new_content:
        return JsonResponse({"error": "You must write something"}, status=400)

    escaped_content = escape(new_content)

    message.content = escaped_content
    message.edited = True
    message.save()

    return JsonResponse({"status": "Message updated"}, status=200)


@login_required
def delete_chat_messages(request, recipient_id):
    """View to delete (hide) chat messages for the authenticated user."""
    recipient = get_object_or_404(User, id=recipient_id)
    user = request.user

    ChatMessage.objects.filter(sender=user, recipient=recipient).update(
        sender_hidden=True
    )
    ChatMessage.objects.filter(sender=recipient, recipient=user).update(
        recipient_hidden=True
    )

    return JsonResponse({"status": "success"})


@login_required
def chat_list(request):
    """View function used to display a list of chat conversations involving the logged-in user."""
    user = request.user

    # Get all conversations involving the logged-in user
    conversations = (
        ChatMessage.objects.filter(Q(sender=user) | Q(recipient=user))
        .values("sender", "recipient")
        .distinct()
    )

    # Get the other users in these conversations
    other_user_ids = set()
    for conv in conversations:
        if conv["sender"] != user.id:
            other_user_ids.add(conv["sender"])
        if conv["recipient"] != user.id:
            other_user_ids.add(conv["recipient"])

    # Fetch details of other users
    users = User.objects.filter(id__in=other_user_ids)

    chat_info = []
    for other_user in users:
        latest_message = (
            ChatMessage.objects.filter(
                Q(sender=other_user, recipient=request.user, recipient_hidden=False)
                | Q(sender=request.user, recipient=other_user, sender_hidden=False)
            )
            .order_by("-created_at")
            .first()
        )

        if latest_message:
            sender_label = _("Sender:")
            if latest_message.sender == request.user:
                sender_name = _("You")
            else:
                sender_name = latest_message.sender.userprofile.profile_name
            message_content = (
                f"{latest_message.content[:20]} ({sender_label} {sender_name})"
            )

            chat_entry = {
                "user": other_user,
                "latest_message": message_content,
                "timestamp": latest_message.created_at,
            }
        else:
            chat_entry = {
                "user": other_user,
                "latest_message": _("No messages yet"),
            }

        chat_info.append(chat_entry)

    chat_info.sort(
        key=lambda x: (x.get("timestamp") is None, x.get("timestamp")), reverse=True
    )

    context = {
        "page_title": _("Chat List :: PlayStyle Compass"),
        "chat_info": chat_info,
    }

    return render(request, "messaging/chat_list.html", context)


@login_required
def block_user(request, user_id):
    """View to add a user to the block list."""
    if request.method == "POST":
        user_profile = request.user.userprofile
        user_to_block = get_object_or_404(UserProfile, user__id=user_id)

        if request.user.id == user_to_block.user.id:
            return JsonResponse({"error": _("You cannot block yourself.")}, status=400)

        if user_to_block.user in user_profile.blocked_users.all():
            return JsonResponse({"message": _("User is already blocked.")})
        else:
            user_profile.blocked_users.add(user_to_block.user)
            return JsonResponse({"message": _("User has been blocked.")})

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def unblock_user(request, user_id):
    """View to remove a user from the block list."""
    if request.method == "POST":
        user_profile = request.user.userprofile
        user_to_unblock = get_object_or_404(UserProfile, user__id=user_id)

        if request.user.id == user_to_unblock.user.id:
            return JsonResponse(
                {"error": _("You cannot unblock yourself.")}, status=400
            )

        if user_to_unblock.user in user_profile.blocked_users.all():
            user_profile.blocked_users.remove(user_to_unblock.user)
            return JsonResponse({"message": _("User has been unblocked.")})
        else:
            return JsonResponse({"message": _("User was not blocked.")})

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def check_block_status(request, user_id):
    """View to check if a user is blocked."""
    user_profile = request.user.userprofile
    user_to_check = get_object_or_404(UserProfile, user__id=user_id)

    is_blocked = user_to_check.user in user_profile.blocked_users.all()
    return JsonResponse({"is_blocked": is_blocked})


@login_required
def block_list(request):
    """View used to display the block list of the user."""
    blocked_users = request.user.userprofile.blocked_users.all()

    context = {
        "page_title": _("Block List :: PlayStyle Compass"),
        "blocked_users": blocked_users,
    }

    return render(request, "messaging/block_list.html", context)


@login_required
def toggle_pin_message(request, message_id):
    """View used to toggle pin/unpin for a chat message."""
    message = get_object_or_404(ChatMessage, id=message_id)

    if request.user in message.pinned_by.all():
        message.pinned_by.remove(request.user)
        action = "unpinned"
    else:
        message.pinned_by.add(request.user)
        action = "pinned"

    return JsonResponse({"status": "success", "action": action})


@login_required
def load_pinned_messages(request, recipient_id):
    """View used to load pinned messages in chat."""
    recipient = get_object_or_404(User, id=recipient_id)

    # Query to get pinned messages sent by the user or the recipient
    pinned_messages_queryset = ChatMessage.objects.filter(
        pinned_by=request.user, recipient=recipient
    ).values(
        "id",
        "content",
        "sender__id",
        "sender__userprofile__profile_name",
        "created_at",
        "file",
        "file_size",
    ) | ChatMessage.objects.filter(
        pinned_by=request.user, sender=recipient
    ).values(
        "id",
        "content",
        "sender__id",
        "sender__userprofile__profile_name",
        "created_at",
        "file",
        "file_size",
    )

    pinned_messages = list(pinned_messages_queryset.order_by("-created_at"))

    # Update the profile name to "You" where the sender is the current user
    for message in pinned_messages:
        if message["sender__id"] == request.user.id:
            message["sender__userprofile__profile_name"] = _("You")

    return JsonResponse(pinned_messages, safe=False)


@login_required
def follow_user(request, user_id):
    """View used to follow users."""
    if request.method == "POST":
        user_to_follow = get_object_or_404(User, id=user_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user, followed=user_to_follow
        )

        if created:
            follower_profile_name = request.user.userprofile.profile_name
            profile_url = reverse("users:view_profile", args=[follower_profile_name])

            message = (
                f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{follower_profile_name}</a> '
                "has started following you!"
            )

            create_notification(
                user_to_follow,
                message=message,
                notification_type="follow",
                profile_url=profile_url,
                follower_profile_name=follower_profile_name,
            )

            message = (
                _("You are now following %s.") % user_to_follow.userprofile.profile_name
            )
        else:
            message = (
                _("You are already following %s.")
                % user_to_follow.userprofile.profile_name
            )

        return JsonResponse({"message": message, "status": "following"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def unfollow_user(request, user_id):
    """View used to unfollow users."""
    if request.method == "POST":
        user_to_unfollow = get_object_or_404(User, id=user_id)
        follow = Follow.objects.filter(
            follower=request.user, followed=user_to_unfollow
        ).first()

        if follow:
            follow.delete()
            message = (
                _("You have unfollowed %s.") % user_to_unfollow.userprofile.profile_name
            )
        else:
            message = (
                _("You are not following %s.")
                % user_to_unfollow.userprofile.profile_name
            )

        return JsonResponse({"message": message, "status": "unfollowing"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def followers_list(request, user_id):
    """View used to display the list of followers for a user."""
    user = get_object_or_404(User, id=user_id)
    followers = Follow.objects.filter(followed=user).select_related("follower")

    followers_with_names = [
        {
            "user": follow.follower,
            "profile_name": follow.follower.userprofile.profile_name,
        }
        for follow in followers
    ]

    context = {
        "page_title": _("Followers :: PlayStyle Compass"),
        "followers": followers_with_names,
        "profile_user": user,
    }

    return render(request, "user_related/followers_list.html", context)


@login_required
def following_list(request, user_id):
    """View used to display the list of users the user is following."""
    user = get_object_or_404(User, id=user_id)
    following = Follow.objects.filter(follower=user).select_related("followed")

    # Create a list of following users with their profile names
    following_with_names = [
        {
            "user": follow.followed,
            "profile_name": follow.followed.userprofile.profile_name,
        }
        for follow in following
    ]

    context = {
        "page_title": _("Following :: PlayStyle Compass"),
        "following": following_with_names,
        "profile_user": user,
    }

    return render(request, "user_related/following_list.html", context)


@login_required
def notification_settings(request):
    """View used to manage notification settings."""
    user_profile = request.user.userprofile

    if request.method == "POST":
        form = NotificationSettingsForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("users:notification_settings")
    else:
        form = NotificationSettingsForm(instance=user_profile)

    context = {
        "page_title": _("Notification Settings :: PlayStyle Compass"),
        "form": form,
    }

    return render(request, "user_related/notification_settings.html", context)


@login_required
def create_global_chat_message(request):
    """View to create/send a global chat message."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    content = request.POST.get("content")

    if not content:
        return JsonResponse({"error": "You must write something"}, status=400)

    user = request.user

    cache_key = f"global_message_count_{user.username}"
    current_time = time.time()

    message_info = cache.get(cache_key, {"count": 0, "timestamps": []})
    message_info["timestamps"] = [
        ts for ts in message_info["timestamps"] if current_time - ts < 15
    ]

    if len(message_info["timestamps"]) >= 8:
        return JsonResponse(
            {
                "error": "You are sending messages too quickly. Please slow down.",
                "rate_limited": True,
            },
            status=429,
        )

    message_info["timestamps"].append(current_time)
    message_info["count"] = len(message_info["timestamps"])
    cache.set(cache_key, message_info, timeout=15)

    global_chat_message = GlobalChatMessage.objects.create(
        sender=user,
        content=content,
        created_at=timezone.now(),
    )

    channel_layer = get_channel_layer()
    channel_layer.group_send(
        "global_chat",
        {
            "type": "chat_message",
            "message": content,
            "sender_id": user.id,
            "sender_name": user.userprofile.profile_name,
            "profile_picture_url": user.userprofile.profile_picture.url,
        },
    )

    return JsonResponse({"status": "Message created"}, status=201)


@login_required
def get_chat_messages(request):
    """View used to get a certain number of global chat messages."""
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 10))

    messages = (
        GlobalChatMessage.objects.all()
        .order_by("-created_at")[offset : offset + limit]
        .annotate(
            sender__userprofile__profile_picture=Concat(
                Value(settings.MEDIA_URL),
                F("sender__userprofile__profile_picture"),
                output_field=CharField(),
            )
        )
        .values(
            "id",
            "created_at",
            "content",
            "sender__id",
            "sender__userprofile__profile_name",
            "sender__userprofile__profile_picture",
        )
    )

    response_data = [
        {
            "id": message["id"],
            "message": message["content"],
            "sender_id": message["sender__id"],
            "sender_name": message["sender__userprofile__profile_name"],
            "profile_picture_url": message["sender__userprofile__profile_picture"],
            "created_at": message["created_at"].isoformat(),
        }
        for message in messages
    ]

    return JsonResponse(response_data, safe=False)


@login_required
def get_private_chat_messages(request, recipient_id):
    """View used to get a specified number of private chat messages."""
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 10))

    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Recipient not found."}, status=404)

    messages = list(
        ChatMessage.objects.filter(
            (Q(sender=request.user, recipient=recipient) & ~Q(sender_hidden=True))
            | (Q(sender=recipient, recipient=request.user) & ~Q(recipient_hidden=True))
        )
        .annotate(
            profile_picture_url=Concat(
                Value(settings.MEDIA_URL),
                F("sender__userprofile__profile_picture"),
                output_field=CharField(),
            ),
            is_pinned=Q(pinned_by__in=[request.user]),
        )
        .order_by("-created_at")
        .values(
            "id",
            "created_at",
            "content",
            "profile_picture_url",
            "sender",
            "edited",
            "file",
            "file_size",
            "is_pinned",
        )[offset : offset + limit]
    )

    response_data = [
        {
            "id": message["id"],
            "message": message["content"],
            "sender_id": message["sender"],
            "profile_picture_url": message["profile_picture_url"],
            "created_at": message["created_at"].isoformat(),
            "edited": message["edited"],
            "file": message["file"],
            "file_size": message["file_size"],
            "is_pinned": message["is_pinned"],
        }
        for message in messages
    ]

    return JsonResponse(response_data, safe=False)


@login_required
def change_language(request):
    if request.method == "POST" and request.content_type == "application/json":
        import json

        data = json.loads(request.body)
        language = data.get("language", "en")
        if language in ["en", "ro"]:
            user_profile = request.user.userprofile
            user_profile.language = language
            user_profile.save()

            translation.activate(language)
            request.session["django_language"] = language

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)
