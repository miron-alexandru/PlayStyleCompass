"""Defines signals for the playstyle_compass app."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Game


@receiver(post_save, sender=Game)
def update_game_score(sender, instance, created, **kwargs):
    """Update the game's score after creation."""
    if created:
        instance.update_score()
