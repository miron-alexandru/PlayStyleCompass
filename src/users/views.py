"""Defines views."""

import time
from datetime import datetime, timedelta
import asyncio
from asgiref.sync import sync_to_async
import json
import random
import ast

from typing import AsyncGenerator
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
from django.conf import settings
from django.contrib.auth.views import LoginView

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
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
from django.utils.safestring import mark_safe
from django.http import (
    JsonResponse,
    HttpResponse,
    Http404,
    HttpRequest,
    StreamingHttpResponse,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import default_token_generator

from playstyle_compass.models import UserPreferences, Review, Game

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
)

from .misc.helper_functions import (
    are_friends,
    check_quiz_time,
    QuizRecommendations,
    get_quiz_questions,
    save_quiz_responses,
    process_chat_notification,
)
from playstyle_compass.helper_functions.views_helpers import (
    paginate_matching_games,
    get_friend_list,
)
from .models import (
    UserProfile,
    FriendList,
    FriendRequest,
    Message,
    Notification,
    QuizUserResponse,
    ChatMessage,
)
from .tokens import account_activation_token


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
    """Cusotm user login view."""

    authentication_form = CustomAuthenticationForm
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("playstyle_compass:index")

        return super().dispatch(request, *args, **kwargs)


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
            message = _(
                "Hello <b>%(user)s</b>, please go to your email <b>%(to_email)s</b> inbox and click on the received activation link to confirm your registration. <b>Note:</b> If you cannot find the email in your inbox, we recommend checking your spam folder."
            ) % {
                "user": user,
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
    else:
        messages.error(request, _("Email address already confirmed!"))


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

    login(request, new_user)
    activate_email(request, new_user, form.cleaned_data.get("email"))

    return redirect("playstyle_compass:index")


@login_required
def delete_account(request):
    """View for deleting a user's account."""
    if request.method == "POST":
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]
            if request.user.check_password(password):
                request.user.delete()
                messages.success(
                    request, _("Your account has been successfully deleted!")
                )
                return redirect("playstyle_compass:index")
            else:
                form.add_error("password", _("Incorrect password. Please try again."))
    else:
        form = DeleteAccountForm()

    context = {"form": form, "page_title": _("Delete Account :: PlayStyle Compass")}

    return render(request, "account_actions/delete_account.html", context)


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
            "You have changed your password, go to the homepage by clicking the button below."
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

        if user_id and user_id != "invalid_user":
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

                        notification = Notification(user=receiver, message=message)
                        notification.save()

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
                        mark_safe(
                            _(
                                "You are now friends with <strong>%(profile_name)s</strong>."
                            )
                            % {
                                "profile_name": friend_request.sender.userprofile.profile_name
                            }
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

                    notification = Notification(
                        user=friend_request.sender, message=message
                    )
                    notification.save()

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
                    mark_safe(
                        _(
                            "You are no longer friends with <strong>%(profile_name)s</strong>."
                        )
                        % {"profile_name": friend_to_remove.userprofile.profile_name}
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
                        mark_safe(
                            _(
                                "You refused to be friends with <strong>%(profile_name)s</strong>."
                            )
                            % {
                                "profile_name": friend_request.sender.userprofile.profile_name
                            }
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

                    notification = Notification(
                        user=friend_request.sender, message=message
                    )
                    notification.save()

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
                    mark_safe(
                        _(
                            "You canceled your friend request for <strong>%(profile_name)s</strong>."
                        )
                        % {"profile_name": receiver.userprofile.profile_name}
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

        is_friend = get_friend_status(request_user, profile_to_view)

        context.update(
            {
                "user_profile": user_profile,
                "is_friend": is_friend,
                "user_id": user.id,
                "user_preferences": user_stats["user_preferences"],
                "user_reviews_count": user_stats["user_reviews_count"],
                "review_likes_count": user_stats["review_likes_count"],
                "show_in_queue": user_stats["user_preferences"].show_in_queue,
                "show_reviews": user_stats["user_preferences"].show_reviews,
                "show_favorites": user_stats["user_preferences"].show_favorites,
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
            return _("Not Friend")
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

    return {
        "user_preferences": user_preferences,
        "user_reviews_count": user_reviews_count,
        "review_likes_count": review_likes_count,
    }


@login_required
def send_message(request, user_id):
    """View used to send messages between users."""
    message_sender = request.user
    message_receiver = get_object_or_404(User, pk=user_id)

    if are_friends(message_sender, message_receiver):
        if request.method == "POST":
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

                message = (
                    f'<a class="notification-profile" title="View User Profile" href="{profile_url}">{user_in_notification}</a> '
                    "just sent you a message!<br>"
                    f'<a class="notification-link" title="Navigate" href="{navigation_url}">View inbox</a>'
                )

                notification = Notification(user=message_receiver, message=message)
                notification.save()

                return redirect(request.META.get("HTTP_REFERER", "users:inbox"))
        else:
            form = MessageForm()
    else:
        messages.error(
            request, _("You have to be friends with someone to send them a message.")
        )
        return redirect("playstyle_compass:index")

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
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("users:view_profile", profile_name=profile_name)
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        "page_title": _("Profile Details :: PlayStyle Compass"),
        "form": form,
    }

    return render(request, "user_related/profile_details.html", context)


@login_required
def chat(request, recipient_id: int):
    """View used to open the chat with a certain user."""
    recipient = get_object_or_404(User, id=recipient_id)

    if not are_friends(request.user, recipient):
        return JsonResponse(
            {"error": "You can only chat with your friends."}, status=403
        )

    request.session["username"] = request.user.username
    request.session["recipient_username"] = recipient.username

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
    username = request.session.get("username")
    recipient_username = request.session.get("recipient_username")

    if not username or not recipient_username:
        return JsonResponse({"error": "Forbidden"}, status=403)

    sender = get_object_or_404(User, username=username)
    recipient = get_object_or_404(User, username=recipient_username)

    if not content:
        return JsonResponse({"error": "You must write something"}, status=400)

    content = escape(content)

    # Rate limiting check -> max 20 messages in 20 seconds
    cache_key = f"message_count_{username}"
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

    ChatMessage.objects.create(sender=sender, recipient=recipient, content=content)
    process_chat_notification(sender, recipient)

    return JsonResponse({"status": "Message created"}, status=201)


@login_required
def edit_message(request, message_id):
    """View to edit a chat message."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    new_content = request.POST.get("content")
    username = request.session.get("username")

    if not username:
        return JsonResponse({"error": "Forbidden"}, status=403)

    sender = get_object_or_404(User, username=username)
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


async def stream_chat_messages(request, recipient_id: int) -> StreamingHttpResponse:
    """View used to stream chat messages between the authenticated user and a specified recipient."""
    recipient = await sync_to_async(get_object_or_404)(User, id=recipient_id)

    async def event_stream():
        async for message in get_existing_messages(request.user, recipient):
            yield message

        last_id = await get_last_message_id(request.user, recipient)
        while True:
            new_messages = (
                ChatMessage.objects.filter(
                    sender__in=[request.user, recipient],
                    recipient__in=[request.user, recipient],
                    id__gt=last_id,
                )
                .annotate(
                    profile_picture_url=Concat(
                        Value(settings.MEDIA_URL),
                        F("sender__userprofile__profile_picture"),
                        output_field=CharField(),
                    )
                )
                .order_by("created_at")
                .values(
                    "id",
                    "created_at",
                    "sender__userprofile__profile_name",
                    "content",
                    "profile_picture_url",
                    "sender__id",
                    "edited"
                )
            )

            async for message in new_messages:
                message["created_at"] = message["created_at"].isoformat()
                message["content"] = escape(message["content"])
                json_message = json.dumps(message, cls=DjangoJSONEncoder)

                yield f"data: {json_message}\n\n"
                last_id = message["id"]
            await asyncio.sleep(0.1)

    async def get_existing_messages(user, recipient) -> AsyncGenerator:
        messages = (
            ChatMessage.objects.filter(
                sender__in=[user, recipient], recipient__in=[user, recipient]
            )
            .filter(
                (Q(sender=user) & Q(sender_hidden=False))
                | (Q(recipient=user) & Q(recipient_hidden=False))
            )
            .annotate(
                profile_picture_url=Concat(
                    Value(settings.MEDIA_URL),
                    F("sender__userprofile__profile_picture"),
                    output_field=CharField(),
                )
            )
            .order_by("created_at")
            .values(
                "id",
                "created_at",
                "sender__userprofile__profile_name",
                "content",
                "profile_picture_url",
                "sender__id",
                "edited"
            )
        )

        async for message in messages:
            message["created_at"] = message["created_at"].isoformat()
            message["content"] = escape(message["content"])
            json_message = json.dumps(message, cls=DjangoJSONEncoder)

            yield f"data: {json_message}\n\n"

    async def get_last_message_id(user, recipient) -> int:
        last_message = await ChatMessage.objects.filter(
            sender__in=[user, recipient], recipient__in=[user, recipient]
        ).alast()
        return last_message.id if last_message else 0

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
