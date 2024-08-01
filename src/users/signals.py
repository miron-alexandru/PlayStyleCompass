"""Defines singals."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from playstyle_compass.models import UserPreferences
from .models import UserProfile, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import UserProfile
from django.utils import timezone

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
            user_group_name,
            {
                "type": "send_notification",
                "id": instance.id,
                "message": instance.message,
                "is_read": instance.is_read,
                "is_active": instance.is_active,
                "timestamp": instance.timestamp,
            },
        )

@receiver(user_logged_in)
def update_user_online_status(sender, request, user, **kwargs):
    UserProfile.objects.update_or_create(user=user, defaults={'is_online': True, 'last_online': None})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_status_{user.id}",
        {
            'type': 'status_update',
            'status': True
        }
    )

@receiver(user_logged_out)
def update_user_offline_status(sender, request, user, **kwargs):
    UserProfile.objects.update_or_create(user=user, defaults={'is_online': False, 'last_online': timezone.now()})

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_status_{user.id}",
        {
            'type': 'status_update',
            'status': False
        }
    )