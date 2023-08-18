from django import forms

from .models import GamingPreferences

class GamingPreferencesForm(forms.ModelForm):
    class Meta:
        model = GamingPreferences
        fields = ['text']
        labels = {'text': ''}