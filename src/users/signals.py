"""Defines singals."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from playstyle_compass.models import UserPreferences
from .models import UserProfile, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async


@receiver(post_save, sender=User)
def create_user_models(sender, instance, created, **kwargs):
    """Create user models."""
    if created:
        if instance.is_superuser:
            user_profile = UserProfile.objects.create(user=instance)
            user_profile.profile_name = "admin"
            user_profile.save()
        UserPreferences.objects.create(user=instance)


post_save.connect(create_user_models, sender=User)


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()

        user = instance.user
        user_group_name = f"user_{user.id}"

        async_to_sync(channel_layer.group_send)(
            user_group_name, {"type": "send_notification", "message": instance.message}
        )
