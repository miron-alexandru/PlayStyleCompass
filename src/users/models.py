"""Defines models."""


from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """User profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    profile_name = models.CharField(max_length=15, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)

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
        return self.timestamp.strftime('%b %d, %Y %I:%M %p')
