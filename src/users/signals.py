from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from playstyle_compass.models import UserPreferences


@receiver(post_save, sender=User)
def create_user_models(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            UserProfile.objects.create(user=instance)
        UserPreferences.objects.create(user=instance)


post_save.connect(create_user_models, sender=User)
