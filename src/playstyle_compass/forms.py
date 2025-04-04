"""Defines forms."""

from django import forms

from .models import (
    Review,
    Game,
    GameList,
    ListReview,
    UserPreferences,
    ListComment,
    Poll,
    PollOption,
)
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


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
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter the title of your game list"),
                "class": "form-control",
            }
        ),
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": _("Enter a description for your game list (optional)"),
                "class": "form-control",
                "rows": 4,
            }
        ),
        required=False,
    )

    games = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text=_("Select games to include in the list."),
    )

    additional_games = forms.CharField(
        label="Additional games (comma-separated)",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter additional game names")}),
    )

    is_public = forms.BooleanField(
        label=_("Make public"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = GameList
        fields = ["title", "description", "games", "additional_games", "is_public"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if instance and instance.game_guids:
            preselected_games = Game.objects.filter(guid__in=instance.game_guids)
            self.fields["games"].initial = preselected_games

        if instance and instance.additional_games:
            self.fields["additional_games"].initial = instance.additional_games

    def clean_additional_games(self):
        additional_games = self.cleaned_data.get("additional_games", "").strip()
        return additional_games

    def save(self, commit=True):
        game_list = super().save(commit=False)
        game_list.game_guids = list(
            self.cleaned_data["games"].values_list("guid", flat=True)
        )
        if commit:
            game_list.save()
        return game_list


class ListReviewForm(forms.ModelForm):
    """Form for submitting a rating and review."""

    class Meta:
        model = ListReview
        fields = ["title", "rating", "review_text"]
        widgets = {
            "rating": forms.Select(choices=[(i, i) for i in range(1, 6)]),
            "review_text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Write your review here..."}
            ),
            "title": forms.TextInput(attrs={"placeholder": "Review Title"}),
        }


class PrivacySettingsForm(forms.ModelForm):
    """Manage privacy settings."""

    class Meta:
        model = UserPreferences
        fields = [
            "show_in_queue",
            "show_reviews",
            "show_favorites",
        ]
        widgets = {
            "show_in_queue": forms.CheckboxInput(),
            "show_reviews": forms.CheckboxInput(),
            "show_favorites": forms.CheckboxInput(),
        }


class ListCommentForm(forms.ModelForm):
    """Form for leaving a comment on a Game List."""

    class Meta:
        model = ListComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": _("Write your comment here..."),
                    "rows": 4,
                }
            ),
        }


class PollForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Option 1"}),
        help_text="",
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "cols": 40,
                "placeholder": "Enter poll description here...",
            }
        ),
        max_length=100,
        help_text="",
    )

    title = forms.CharField(
        max_length=50,
        required=True,
        help_text="",
        widget=forms.TextInput(attrs={"placeholder": "Enter poll title..."}),
    )
    duration = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=7,
        widget=forms.NumberInput(attrs={"placeholder": "Duration in days (1-7)"}),
    )
    is_public = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Is this poll public?"),
    )

    class Meta:
        model = Poll
        fields = ["title", "description", "options", "duration", "is_public"]

    def clean_options(self):
        options = self.cleaned_data["options"]
        option_list = [opt.strip() for opt in options.splitlines() if opt.strip()]
        if len(option_list) > 5:
            raise forms.ValidationError(_("You can only add up to 5 options."))
        return options

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")
        return timedelta(days=duration)


class VoteForm(forms.Form):
    option = forms.ModelChoiceField(
        queryset=PollOption.objects.none(), widget=forms.RadioSelect
    )

    def __init__(self, poll, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option"].queryset = poll.options.all()
