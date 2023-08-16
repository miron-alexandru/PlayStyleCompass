from django.db import models
from django.contrib.auth.models import User

class GamingPreferences(models.Model):
    """A topic the user is learning about."""
    id = models.BigAutoField(primary_key=True)
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gaming_history = models.TextField(blank=True)
    favorite_genres = models.CharField(max_length=255, blank=True)
    platforms = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username
