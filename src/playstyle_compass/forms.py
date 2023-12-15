"""Defines forms."""

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form to write a review for a game."""

    class Meta:
        model = Review
        fields = ["review_deck", "review_description", "score"]
        labels = {
            "review_deck": "Review Title",
            "review_description": "Review Summary",
            "score": "Your Rating",
        }
        widgets = {
            "review_deck": forms.TextInput(
                attrs={
                    "placeholder": "Enter a brief title for your review...",
                    "autofocus": "autofocus",
                }
            ),
            "review_description": forms.Textarea(
                attrs={
                    "placeholder": "Share your detailed review of the game, including your thoughts on gameplay, graphics, storyline, and overall experience..."
                }
            ),
        }
