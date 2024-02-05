"""Defines forms."""

from django import forms

from .models import Review
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.ModelForm):
    """Form to write a review for a game."""

    class Meta:
        model = Review
        fields = ["review_deck", "review_description", "score"]
        labels = {
            "review_deck": _("Review Title"),
            "review_description": _("Review"),
            "score": _("Your Rating"),
        }
        widgets = {
            "review_deck": forms.TextInput(
                attrs={
                    "placeholder": _("Enter a brief title for your review..."),
                    "autofocus": "autofocus",
                }
            ),
            "review_description": forms.Textarea(
                attrs={
                    "placeholder": _("Share your detailed review of the game, including your thoughts on gameplay, graphics, storyline, and overall experience...")
                }
            ),
        }
