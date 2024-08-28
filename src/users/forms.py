"""Defines forms."""

import os
import re
from io import BytesIO
import uuid
from PIL import Image
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    AuthenticationForm,
)

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField

from .models import UserProfile, ContactMessage, Message, UserProfile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from utils.constants import GAMING_COMMITMENT_CHOICES, PLATFORM_CHOICES, GENRE_CHOICES
from django.core.files.storage import default_storage


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form."""

    error_messages = {
        "invalid_login": _(
            "Incorrect username or password. Please make sure you entered your  username and password correctly."
        ),
    }
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "",
                "autofocus": "autofocus",
                "autocomplete": "username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "", "autocomplete": "current-password"}
        ),
    )


class CustomRegistrationForm(UserCreationForm):
    """Custom registration form."""

    profile_name = forms.CharField(
        label="Profile Name",
        help_text=_(
            "Choose nickname that will be shown to other users on the platform. This name is not used for login."
        ),
        widget=forms.TextInput(attrs={"autofocus": "autofocus", "placeholder": ""}),
        max_length=32,
    )
    username = forms.CharField(
        help_text="",
        widget=forms.TextInput(attrs={"placeholder": "", "autocomplete": "username"}),
        max_length=32,
    )

    email = forms.EmailField(
        label="Email",
        help_text="",
        widget=forms.EmailInput(attrs={"placeholder": "", "autocomplete": "email"}),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "", "autocomplete": "new-password"}
        ),
        help_text="",
    )

    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(
            attrs={"placeholder": "", "autocomplete": "new-password"}
        ),
        help_text=_("Enter the same password as before for verification."),
    )

    captcha = ReCaptchaField(
        error_messages={"required": _("Please complete reCAPTCHA.")}
    )

    class Meta:
        model = User
        fields = [
            "profile_name",
            "username",
            "email",
            "password1",
            "password2",
            "captcha",
        ]

    def clean_username(self):
        """Clean username."""
        username = self.cleaned_data["username"]

        if len(username) < 4:
            raise forms.ValidationError(
                _("Username should be at least 4 characters long.")
            )

        if not re.match("^[a-zA-Z0-9]+$", username):
            raise forms.ValidationError(
                _("Username should only contain letters and numbers.")
            )

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("This username is already in use."))
        return username

    def clean_email(self):
        """Clean email."""
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email address is already in use."))
        return email

    def clean_profile_name(self):
        """Clean profile name."""
        profile_name = self.cleaned_data["profile_name"]

        if len(profile_name) < 3:
            raise forms.ValidationError(
                _("Profile name should be at least three characters long.")
            )

        if not re.match("^[a-zA-Z0-9]+$", profile_name):
            raise forms.ValidationError(
                _("Profile name should only contain letters and numbers.")
            )

        if UserProfile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError(_("This profile name is already in use."))

        return profile_name


class DeleteAccountForm(forms.Form):
    """Custom delete account form."""

    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"placeholder": ""}),
    )


class EmailChangeForm(forms.ModelForm):
    """Custom email change form."""

    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    current_email = forms.EmailField(
        label="Current Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control", "readonly": True}),
        required=False,
    )

    new_email = forms.EmailField(
        label="New Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    confirm_email = forms.EmailField(
        label="Confirm New Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["email"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        """Clean current password."""
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_("Current password is incorrect."))
        return current_password

    def clean_new_email(self):
        """Clean new email."""
        new_email = self.cleaned_data.get("new_email")

        if new_email:
            if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError(_("This email address is already in use."))

            if new_email == self.user.email:
                raise forms.ValidationError(
                    _("New email address cannot be the current one.")
                )

        return new_email

    def clean_confirm_email(self):
        """Clean confirm email."""
        confirm_email = self.cleaned_data["confirm_email"]
        new_email = self.cleaned_data.get("new_email")

        if new_email and new_email != confirm_email:
            raise forms.ValidationError(_("New email addresses must match."))

        return confirm_email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Password change form."""

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_new_password1(self):
        """Validate the new password1."""
        new_password1 = self.cleaned_data.get("new_password1")
        validate_password(new_password1)

        return new_password1

    def clean_new_password2(self):
        """Validate new password2."""
        new_password2 = self.cleaned_data.get("new_password2")
        validate_password(new_password2)

        return new_password2


class CustomClearableFileInput(forms.ClearableFileInput):
    """Custom file input form."""

    template_name = "widgets/custom_change_img.html"


class ProfilePictureForm(forms.ModelForm):
    """Custom profile picture form."""

    class Meta:
        model = UserProfile
        fields = ["profile_picture"]

    profile_picture = forms.ImageField(
        required=False,
        widget=CustomClearableFileInput(),
        label=" ",
    )

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.profile_picture:
            # Delete the old profile picture if it exists
            self.delete_old_profile_picture(instance)

            # Resize and save the new profile picture
            self.resize_image(instance.profile_picture)

        if commit:
            instance.save()

        return instance

    def delete_old_profile_picture(self, instance):
        """Delete the old profile picture if it exists."""
        if instance.pk:
            old_profile_picture = UserProfile.objects.get(pk=instance.pk).profile_picture
            if old_profile_picture:
                # Use the storage backend to check if the file exists and delete it
                if default_storage.exists(old_profile_picture.name):
                    default_storage.delete(old_profile_picture.name)

    def resize_image(self, image_field):
        """Resize the image."""
        with Image.open(image_field) as image:
            max_size = (250, 250)
            image.thumbnail(max_size, Image.LANCZOS)

            original_name = os.path.basename(image_field.name)
            self.processed_image_to_file(image, image_field, original_name)

    def processed_image_to_file(self, image, image_field, original_name=None):
        """Convert a processed image to a file."""
        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")

        content_file = ContentFile(image_buffer.getvalue())

        # Generate filename with timestamp and user's unique ID
        timestamp = timezone.now().strftime("%Y.%m.%d.%H.%M")
        user_id = self.instance.user.id
        new_name = f"profile_picture_{timestamp}_{user_id}.png"

        image_field.save(new_name, content_file, save=False)


class ContactForm(forms.ModelForm):
    """Custom contact form."""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "", "autofocus": "autofocus"}
            ),
            "email": forms.EmailInput(attrs={"placeholder": ""}),
            "subject": forms.TextInput(attrs={"placeholder": ""}),
            "message": forms.Textarea(attrs={"placeholder": ""}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Profile name update form."""

    profile_name = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}),
    )

    class Meta:
        model = UserProfile
        fields = ["profile_name"]

    def clean_profile_name(self):
        """Clean profile name."""
        profile_name = self.cleaned_data.get("profile_name")

        if not re.match("^[a-zA-Z0-9]+$", profile_name):
            raise forms.ValidationError(
                _("Profile name should only contain letters and numbers.")
            )

        if len(profile_name) < 3:
            raise forms.ValidationError(
                _("Profile name should be at least three characters long.")
            )

        if profile_name.lower() == self.instance.profile_name.lower():
            raise forms.ValidationError(
                _("The new profile name is the same as the existing one.")
            )

        if (
            UserProfile.objects.filter(profile_name=profile_name)
            .exclude(user=self.instance.user)
            .exists()
        ):
            raise forms.ValidationError(_("This profile name is already in use."))

        return profile_name


class MessageForm(forms.ModelForm):
    """Message form."""

    class Meta:
        model = Message
        fields = ["title", "message"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "", "autofocus": "autofocus"}
            ),
            "message": forms.Textarea(attrs={"placeholder": ""}),
        }


class QuizForm(forms.Form):
    """QuizForm used to display questions with their options."""

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choices = [
                ("option1", question.option1),
                ("option2", question.option2),
                ("option3", question.option3),
                ("option4", question.option4),
            ]
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
            )


class GenreField(forms.MultipleChoiceField):
    def clean(self, value):
        if not value:
            return ""
        return ",".join(value)


class UserProfileForm(forms.ModelForm):
    """User Profile Form used to create user profile data."""

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "favorite_game",
            "favorite_character",
            "gaming_commitment",
            "main_gaming_platform",
            "social_media",
            "gaming_genres",
            "gaming_setup",
            "favorite_franchise",
            "last_finished_game",
            "streaming_preferences",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "cols": 50,
                    "autofocus": "autofocus",
                    "placeholder": _("Tell us a little about yourself..."),
                }
            ),
            "favorite_game": forms.TextInput(
                attrs={"placeholder": _("Enter your favorite game...")}
            ),
            "favorite_character": forms.TextInput(
                attrs={"placeholder": _("Enter your favorite character...")}
            ),
            "gaming_commitment": forms.Select(choices=GAMING_COMMITMENT_CHOICES),
            "main_gaming_platform": forms.Select(choices=PLATFORM_CHOICES),
            "social_media": forms.TextInput(
                attrs={"placeholder": _("Enter your social media handle...")}
            ),
            "gaming_setup": forms.Textarea(
                attrs={
                    "rows": 6,
                    "cols": 50,
                    "placeholder": _("Describe your gaming setup..."),
                }
            ),
            "favorite_franchise": forms.TextInput(
                attrs={"placeholder": _("Enter your favorite franchise...")}
            ),
            "last_finished_game": forms.TextInput(
                attrs={"placeholder": _("What's the most recent game you finished?")}
            ),
            "streaming_preferences": forms.TextInput(
                attrs={"placeholder": _("What is your preferred streaming platform?")}
            ),
        }

    gaming_genres = forms.MultipleChoiceField(
        choices=GENRE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False
    )

    def clean_gaming_genres(self):
        genres = self.cleaned_data.get("gaming_genres")
        if len(genres) > 3:
            raise forms.ValidationError(_("You can only select up to 3 genres."))
        return ", ".join(genres) if genres else ""

    def clean_social_media(self):
        social_media = self.cleaned_data.get("social_media")
        if social_media:
            regex_pattern = r"^(https?:\/\/)?(www\.)?(facebook|twitter|instagram|linkedin|x|reddit|youtube|tiktok|discord|twitch)\.com\/.+?$"
            if not re.match(regex_pattern, social_media):
                raise forms.ValidationError(
                    _("Please enter a valid social media link.")
                )
        return social_media
