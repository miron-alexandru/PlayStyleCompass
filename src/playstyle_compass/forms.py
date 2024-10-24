"""Defines forms."""

from django import forms

from .models import Review, Game, GameList
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
                    "placeholder": _(
                        "Share your detailed review of the game, including your thoughts on gameplay, graphics, storyline, and overall experience..."
                    )
                }
            ),
        }


class GameListForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter the title of your game list'),
            'class': 'form-control',
        }),
        required=True
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': _('Enter a description for your game list (optional)'),
            'class': 'form-control',
            'rows': 4,
        }),
        required=False
    )
    
    games = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text=_("Select games to include in the list.")
    )

    additional_games = forms.CharField(
        label="Add additional games (comma-separated)", 
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter additional game names")})
    )

    class Meta:
        model = GameList
        fields = ['title', 'description', 'games']

    def save(self, commit=True):
        game_list = super().save(commit=False)
        game_list.game_guids = list(self.cleaned_data['games'].values_list('guid', flat=True))
        if commit:
            game_list.save()
        return game_list

