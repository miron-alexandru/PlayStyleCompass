"""Defines models."""


from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    """User profile model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    profile_name = models.CharField(max_length=15, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)

    def clean(self):
        profile_name = self.profile_name
        existing_profiles = UserProfile.objects.filter(profile_name=profile_name).exclude(user=self.user)

        if existing_profiles.exists():
            raise ValidationError("This profile name is already in use by another user. Please choose a different one.")

    def __str__(self):
        return self.user.username


class ContactMessage(models.Model):
    """Contact message model."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def formatted_timestamp(self):
        """Return the timestap formatted."""
        return self.timestamp.strftime("%b %d, %Y %I:%M %p")
