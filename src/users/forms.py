from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(
        help_text="")
    email = forms.EmailField(
        label="Email",
        help_text="")
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=(""
        )
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
