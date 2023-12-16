"""Defines views."""

from datetime import timedelta
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login,
    update_session_auth_hash,
)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.views import LoginView

from django.template.loader import render_to_string
from django.templatetags.static import static
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import (
    force_bytes,
    force_str,
)
from django.core.mail import EmailMessage
from django.utils.safestring import mark_safe
from django.http import JsonResponse, HttpResponse, Http404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import default_token_generator

from .forms import (
    CustomRegistrationForm,
    DeleteAccountForm,
    EmailChangeForm,
    CustomPasswordChangeForm,
    ProfilePictureForm,
    ContactForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
)

from .misc.helper_functions import are_friends
from .models import UserProfile, FriendList, FriendRequest
from .tokens import account_activation_token

from playstyle_compass.models import UserPreferences, Review


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View used to update the profile name for users."""

    model = UserProfile
    template_name = "account_actions/profile_name_update.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("playstyle_compass:index")

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def dispatch(self, request, *args, **kwargs):
        if last_update_time := self.request.user.userprofile.name_last_update_time:
            one_hour_ago = timezone.now() - timedelta(hours=1)
            if last_update_time > one_hour_ago:
                messages.error(
                    self.request, "You can only update your profile name once per hour."
                )
                return redirect(
                    request.META.get("HTTP_REFERER", "playstyle_compass:index")
                )

        return super().dispatch(request, *args, **kwargs)

    def update_user_reviews(self, new_profile_name):
        user_reviews = Review.objects.filter(user=self.request.user)

        for review in user_reviews:
            review.reviewers = new_profile_name
            review.save()

    def form_valid(self, form):
        new_profile_name = self.object.profile_name

        self.object = form.save(commit=False)
        self.object.name_last_update_time = timezone.now()
        self.object.save()

        self.update_user_reviews(new_profile_name)

        return super().form_valid(form)


class CustomLoginView(LoginView):
    """Cusotm user login view."""

    authentication_form = CustomAuthenticationForm
    template_name = "registration/login.html"


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

        messages.success(request, "Thank you for your email confirmation!")
        return redirect("playstyle_compass:index")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect("playstyle_compass:index")


@login_required
def activateEmail(request, user, to_email):
    """Send activation email to users."""
    mail_subject = "Activate your user account."
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
        message = (
            f"Hello <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on "
            f"received activation link to confirm your registration. \
                  <b>Note:</b> If you cannot find the email in your inbox, we recommend checking your spam folder."
        )
        messages.success(request, mark_safe(message))
    else:
        messages.error(
            request,
            f"Problem sending email to {to_email}, check if you typed it correctly.",
        )


@login_required
def resend_activation_link(request):
    """Resend email activation link to the user."""
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "error_message": "Invalid request method"}
        )

    email = request.user.email
    user = User.objects.get(email=email)
    activateEmail(request, user, email)

    return JsonResponse({})


def register(request):
    """View function for user registration."""
    if request.method == "POST":
        form = CustomRegistrationForm(data=request.POST)

        if form.is_valid():
            return register_user(form, request)
    else:
        form = CustomRegistrationForm()

    context = {"form": form, "page_title": "Register :: PlayStyle Compass"}

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

    user_profile.save()
    new_user.save()

    login(request, new_user)
    activateEmail(request, new_user, form.cleaned_data.get("email"))

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
                messages.success(request, "Your account has been successfully deleted!")
                return redirect("playstyle_compass:index")
            else:
                form.add_error("password", "Incorrect password. Please try again.")

    else:
        form = DeleteAccountForm()

    context = {"form": form, "page_title": "Delete Account :: PlayStyle Compass"}

    return render(request, "account_actions/delete_account.html", context)


@login_required
def change_email(request):
    """View for email change with verification."""
    if request.method == "POST":
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_email = form.cleaned_data["new_email"]
            token = default_token_generator.make_token(request.user)
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))

            request.session["email_change_temp"] = new_email
            request.session["email_change_token"] = token

            confirm_url = request.build_absolute_uri(
                reverse(
                    "users:confirm_email_change", kwargs={"uidb64": uid, "token": token}
                )
            )

            subject = "Confirm Email Change"
            from_email = settings.DEFAULT_FROM_EMAIL
            message = render_to_string(
                "account_actions/confirm_email_change.txt",
                {"confirm_url": confirm_url, "new_email": new_email},
            )
            send_mail(subject, message, from_email, [request.user.email])

            return redirect("users:change_email_done")
    else:
        form = EmailChangeForm(
            user=request.user, initial={"current_email": request.user.email}
        )

    context = {"form": form, "page_title": "Change Email :: PlayStyle Compass"}

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

    return HttpResponse("Invalid token for email change.")


@login_required
def change_email_success(request):
    """View for email change success."""
    new_email = request.user.email
    messages.success(request, "Email Address successfully changed!")
    context = {
        "page_title": "Email Change Success :: PlayStyle Compass",
        "response": "You have successfully changed your email address, go to the homepage by clicking the button below.",
        "additional_message": new_email,
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def change_email_done(request):
    """View for email change confirmation."""
    messages.success(request, "Confirmation email successfully sent!")
    context = {
        "page_title": "Email Change Done :: PlayStyle Compass",
        "response": "An email confirmation has been sent to your current email address. Please check your inbox and click the link provided to confirm the email change.",
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def change_password(request):
    """View for changing a user's password."""
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            password1 = form.cleaned_data["new_password1"]
            password2 = form.cleaned_data["new_password2"]

            if password1 == password2:
                if not request.user.check_password(password1):
                    request.user.set_password(password1)
                    request.user.save()

                    update_session_auth_hash(request, request.user)
                    return redirect("users:change_password_done")
                else:
                    messages.error(
                        request, "New password must be different from the old password!"
                    )
            else:
                form.add_error("new_password2", "New passwords must match.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        "form": form,
        "page_title": "Change Password :: PlayStyle Compass",
    }

    return render(request, "account_actions/password_change_form.html", context)


@login_required
def change_password_done(request):
    """View for password change confirmation."""
    messages.success(request, "Password Changed Successfully!")
    context = {
        "page_title": "Password Change Done :: PlayStyle Compass",
        "response": "You have changed your password, go to the homepage by clicking the button below.",
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
        "page_title": "Change Profile Picture :: PlayStyle Compass",
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

    context = {"form": form, "page_title": "Contact Us :: PlayStyle Compass"}

    return render(request, "account_actions/contact.html", context)


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
    messages.success(request, "Your message has been successfully submitted!")
    context = {
        "page_title": "Contact Us Done :: PlayStyle Compass",
        "response": "Thank you for contacting us! Our team will review it within 48 hours and get back to you as soon as possible. \
    Go to the homepage by clicking the button below.",
    }
    return render(request, "account_actions/change_succeeded.html", context)


@login_required
def friends_list_view(request, *args, **kwargs):
    """View to display the friends list."""
    viewer = request.user
    context = {}

    if not viewer.is_authenticated:
        return HttpResponse("You must be authenticated to view the friends list.")

    user_id = kwargs.get("user_id")
    this_user = get_object_or_404(User, pk=user_id)

    if viewer != this_user:
        return HttpResponse("You cannot view the friends list of another user.")

    friend_list, created = FriendList.objects.get_or_create(user=this_user)
    auth_user_friend_list = FriendList.objects.get(user=request.user)

    friends = [(friend, auth_user_friend_list) for friend in friend_list.friends.all()]

    context = {
        "page_title": "Friends List :: PlayStyle Compass",
        "this_user": this_user,
        "friends": friends,
    }

    return render(request, "account_actions/friends_list.html", context)


@login_required
def friend_requests_view(request, *args, **kwargs):
    """View to see all friend requests."""
    user = request.user

    if not user.is_authenticated:
        return redirect("playstyle_compass:index")

    user_id = kwargs.get("user_id")
    account = User.objects.get(pk=user_id)

    if account != user:
        return HttpResponse("You can't view the friend requests of another user.")

    friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
    user_sent_friend_requests = FriendRequest.objects.filter(
        sender=user, is_active=True
    )

    context = {
        "page_title": "Friend Requests :: PlayStyle Compass",
        "friend_requests": friend_requests,
        "user_sent_friend_requests": user_sent_friend_requests,
    }

    return render(request, "account_actions/friend_requests.html", context)


def send_friend_request(request, *args, **kwargs):
    """View to send a friend request."""
    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("user_id", "invalid_user")

        if user_id and user_id != "invalid_user":
            receiver_queryset = User.objects.filter(pk=user_id)

            if receiver_queryset.exists():
                receiver = receiver_queryset.first()

                if are_friends(user, receiver):
                    result[
                        "message"
                    ] = f"<strong>{receiver.userprofile.profile_name}</strong> is already in your friends list."
                elif user == receiver:
                    result[
                        "message"
                    ] = f"You cannot send a friend request to <strong>yourself.</strong>"
                else:
                    friend_requests = FriendRequest.objects.filter(
                        sender=user, receiver=receiver, is_active=True
                    )

                    if friend_requests.exists():
                        result["message"] = "You already sent them a friend request."
                    else:
                        try:
                            friend_request = FriendRequest.objects.get(
                                sender=user, receiver=receiver
                            )
                            friend_request.is_active = True
                            friend_request.save()
                        except FriendRequest.DoesNotExist:
                            friend_request = FriendRequest(
                                sender=user, receiver=receiver, is_active=True
                            )
                            friend_request.save()

                        result["message"] = "Friend request sent."
            else:
                result[
                    "message"
                ] = "The user does not exist or has deleted their account."

        else:
            result["message"] = "The user does not exist or has deleted their account."
    else:
        result["message"] = "You must be logged in to send a friend request."

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def accept_friend_request(request, *args, **kwargs):
    """View to accept a friend request."""
    user = request.user
    result = {}

    if request.method == "GET" and user.is_authenticated:
        if friend_request_id := kwargs.get("friend_request_id"):
            friend_request = get_object_or_404(FriendRequest, pk=friend_request_id)

            if friend_request.receiver == user:
                try:
                    friend_request.accept()
                    friend_request.delete()
                    result["message"] = "Friend request accepted."
                    messages.success(
                        request,
                        mark_safe(
                            f"You are now friends with <strong>{friend_request.sender.userprofile.profile_name}</strong>."
                        ),
                    )
                except Exception as e:
                    result["message"] = str(e)
            else:
                result["message"] = "That is not your request to accept."
        else:
            result["message"] = "Unable to accept that friend request."
    else:
        result["message"] = "You must be authenticated to accept a friend request."

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
                result["message"] = "Successfully removed that friend."
                messages.success(
                    request,
                    mark_safe(
                        f"You are no longer friends with <strong>{friend_to_remove.userprofile.profile_name}</strong>."
                    ),
                )
            except Exception as e:
                result["message"] = str(e)
        else:
            result["message"] = "There was an error. Unable to remove that friend."
    else:
        result["message"] = "You must be authenticated to remove a friend."

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
                    result["message"] = "Friend request declined."
                    messages.success(
                        request,
                        mark_safe(
                            f"You refused to be friends with <strong>{friend_request.sender.userprofile.profile_name}</strong>."
                        ),
                    )
                except Exception as e:
                    result["message"] = str(e)
            else:
                result["message"] = "That is not your friend request to decline."
        else:
            result["message"] = "Unable to decline that friend request."
    else:
        result["message"] = "You must be authenticated to decline a friend request."

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def cancel_friend_request(request):
    """View to cancel a friend request."""
    user = request.user
    result = {}

    if request.method == "POST" and user.is_authenticated:
        if receiver_user_id := request.POST.get("receiver_user_id"):
            receiver = get_object_or_404(User, pk=receiver_user_id)
            try:
                friend_requests = FriendRequest.objects.filter(
                    sender=user, receiver=receiver, is_active=True
                )
            except FriendRequest.DoesNotExist:
                result["message"] = "Nothing to cancel. Friend request does not exist."
            else:
                for friend_request in friend_requests:
                    friend_request.cancel()

                result["message"] = "Friend request canceled."
                messages.success(
                    request,
                    mark_safe(
                        f"You canceled your friend request for <strong>{receiver.userprofile.profile_name}</strong>."
                    ),
                )
        else:
            result["message"] = "Unable to cancel that friend request."
    else:
        result["message"] = "You must be authenticated to cancel a friend request."

    return HttpResponse(json.dumps(result), content_type="application/json")


def view_profile(request, profile_name):
    """View used to view the profile of users."""
    context = {"page_title": "User Profile :: PlayStyle Compass"}

    try:
        user_profile = get_object_or_404(UserProfile, profile_name=profile_name)
        user = get_object_or_404(User, id=user_profile.user.id)

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
            }
        )

    except Http404:
        messages.error(request, "The user does not exist or has deleted their account.")
        return redirect(request.META.get("HTTP_REFERER", "playstyle_compass:index"))

    return render(request, "account_actions/user_profile.html", context)


def get_friend_status(request_user, profile_to_view):
    """Determine the friend status."""
    if request_user.is_authenticated:
        if request_user == profile_to_view:
            return "You"
        elif are_friends(request_user, profile_to_view):
            return "Friend"
        else:
            return "Not Friend"
    else:
        return None


def get_user_stats(user):
    user_preferences = UserPreferences.objects.get(user=user)

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
