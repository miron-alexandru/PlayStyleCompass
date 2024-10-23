"""Defines singals."""

import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from playstyle_compass.models import UserPreferences
from .models import UserProfile, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
import pytz


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not getattr(instance, "_profile_created", False):
        # Check if the user already has a UserProfile
        if not UserProfile.objects.filter(user=instance).exists():
            base_name = f"Player_{random.randint(1000, 9999)}"

            unique_name = base_name
            while UserProfile.objects.filter(profile_name=unique_name).exists():
                suffix = "".join(
                    random.choices(string.ascii_letters + string.digits, k=4)
                )
                unique_name = f"Player_{random.randint(1000, 9999)}_{suffix}"

            user_profile = UserProfile(
                user=instance,
                profile_name=unique_name,
                profile_picture="profile_pictures/default_pfp/default_profile_picture.png",
                timezone="",
            )
            user_profile.save()


@receiver(post_save, sender=User)
def create_user_models(sender, instance, created, **kwargs):
    """Create user models."""
    if created:
        if instance.is_superuser:
            user_profile, created = UserProfile.objects.get_or_create(user=instance)
            if created:
                user_profile.profile_name = "admin"
                user_profile.save()

        user_preferences = UserPreferences.objects.create(user=instance)
        user_preferences.quiz_recommendations = []
        user_preferences.save()


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
                "delivered": instance.delivered,
                "notification_type": instance.notification_type,
            },
        )


@receiver(user_logged_in)
def update_user_online_status(sender, request, user, **kwargs):
    user_profile, created = UserProfile.objects.update_or_create(
        user=user, defaults={"is_online": False, "last_online": timezone.now()}
    )

    last_online = get_last_online(user_profile)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_status_{user.id}",
        {"type": "status_update", "status": True, "last_online": last_online},
    )


@receiver(user_logged_out)
def update_user_offline_status(sender, request, user, **kwargs):
    # Extract the UserProfile object from the tuple
    user_profile, created = UserProfile.objects.update_or_create(
        user=user, defaults={"is_online": False, "last_online": timezone.now()}
    )

    last_online = get_last_online(user_profile)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_status_{user.id}",
        {"type": "status_update", "status": False, "last_online": last_online},
    )


def get_last_online(user_profile):
    """Return formatted last_online time based on user_profile's timezone."""
    last_online = user_profile.last_online
    user_timezone = user_profile.timezone

    if last_online and user_timezone:
        user_tz = pytz.timezone(user_timezone)

        if last_online.tzinfo is None:
            last_online = timezone.make_aware(
                last_online, timezone.get_default_timezone()
            )

        last_online = last_online.astimezone(user_tz)
        return last_online.strftime("%B %d, %Y, %I:%M %p")

    return None
