from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from .models import UserProfile, ContactMessage
from django.contrib.auth.views import LoginView

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from captcha.fields import ReCaptchaField


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": _("Incorrect username or password. Please make sure you entered your  username and password correctly."),
    }
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '', 'autofocus': 'autofocus'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': ''}),
        )

class CustomRegistrationForm(UserCreationForm):
    profile_name = forms.CharField(
        label="Profile Name",
        help_text="Choose nickname that will be shown to other users on the site. This name is not used for login.",
        widget=forms.TextInput(attrs={'autofocus': 'autofocus', 'placeholder': ''}),
    )
    username = forms.CharField(
        help_text="",
        widget=forms.TextInput(attrs={'placeholder': ''}))
    email = forms.EmailField(
        label="Email",
        help_text="",
        widget=forms.EmailInput(attrs={'placeholder': ''}),)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': ''}),
        help_text=(""
        )
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={'placeholder': ''}),
        help_text="Enter the same password as before, for verification."
    )
    captcha = ReCaptchaField(
        error_messages={
            'required': 'Please complete reCAPTCHA.'
        }
    )

    class Meta:
        model = User
        fields = ['profile_name', 'username', 'email', 'password1', 'password2', 'captcha']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
    )

class EmailChangeForm(forms.ModelForm):
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    
    current_email = forms.EmailField(
        label='Current Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False,
    )

    new_email = forms.EmailField(
        label='New Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    confirm_email = forms.EmailField(
        label='Confirm New Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return new_email

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email")
        confirm_email = cleaned_data.get("confirm_email")

        if new_email != confirm_email:
            raise forms.ValidationError("New email addresses must match.")

        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password2')
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password1


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'widgets/custom_change_img.html'

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

    profile_picture = forms.ImageField(
        required=False,
        widget=CustomClearableFileInput(),
        label=' ',
    )

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '', 'autofocus': 'autofocus'}),
            'email': forms.EmailInput(attrs={'placeholder': ''}),
            'subject': forms.TextInput(attrs={'placeholder': ''}),
            'message': forms.Textarea(attrs={'placeholder': ''}),
        }