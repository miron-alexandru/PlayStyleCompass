"""Defines forms."""

from django import forms

from .models import GamingPreferences

class GamingPreferencesForm(forms.ModelForm):
    """A form for collecting gaming preferences from users."""

    class Meta:
        model = GamingPreferences
        fields = ['text']
        labels = {'text': ''}
