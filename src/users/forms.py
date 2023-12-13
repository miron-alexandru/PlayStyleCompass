"""Defines forms."""

import os
from PIL import Image
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    AuthenticationForm,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from captcha.fields import ReCaptchaField

from .models import UserProfile, ContactMessage


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
        help_text="Choose nickname that will be shown to other users on the site. This name is not used for login.",
        widget=forms.TextInput(attrs={"autofocus": "autofocus", "placeholder": ""}),
    )
    username = forms.CharField(
        help_text="",
        widget=forms.TextInput(attrs={"placeholder": "", "autocomplete": "username"}),
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
        help_text=(""),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(
            attrs={"placeholder": "", "autocomplete": "new-password"}
        ),
        help_text="Enter the same password as before, for verification.",
    )
    captcha = ReCaptchaField(error_messages={"required": "Please complete reCAPTCHA."})

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

    def clean_email(self):
        """Clean email."""
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_profile_name(self):
        """Clean profile name."""
        profile_name = self.cleaned_data["profile_name"]
        if UserProfile.objects.filter(profile_name=profile_name).exists():
            raise forms.ValidationError("This profile name is already in use.")
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
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean_new_email(self):
        """Clean new email."""
        new_email = self.cleaned_data.get("new_email")

        if new_email:
            if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("This email address is already in use.")

            if new_email == self.user.email:
                raise forms.ValidationError(
                    "New email address cannot be the current one."
                )

        return new_email

    def clean_confirm_email(self):
        """Clean confirm email."""
        confirm_email = self.cleaned_data["confirm_email"]
        new_email = self.cleaned_data.get("new_email")

        if new_email and new_email != confirm_email:
            raise forms.ValidationError("New email addresses must match.")

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
        """Clean new password."""
        return self.clean_passwords("new_password1")

    def clean_new_password2(self):
        """Clean new password confirmation."""
        return self.clean_passwords("new_password2")

    def clean_passwords(self, arg0):
        password1 = self.cleaned_data.get(arg0)
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password1


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
            self.resize_image(instance.profile_picture)

        if commit:
            instance.save()

        return instance

    def resize_image(self, image_field):
        """Resize the image."""
        image = Image.open(image_field)
        max_size = (300, 300)
        image.thumbnail(max_size, Image.ANTIALIAS)

        original_name = os.path.basename(image_field.name)
        self.processed_image_to_file(image, image_field, original_name)


    def processed_image_to_file(self, image, image_field, original_name=None):
        """Convert a processed image to a file."""
        from django.core.files.base import ContentFile
        from io import BytesIO
        import os
        import uuid

        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")

        content_file = ContentFile(image_buffer.getvalue())

        if original_name:
            new_name = original_name
        else:
            new_name = f"{uuid.uuid4()}.png"

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
        if (
            UserProfile.objects.filter(profile_name=profile_name)
            .exclude(user=self.instance.user)
            .exists()
        ):
            raise forms.ValidationError("This profile name is already in use.")
        return profile_name
