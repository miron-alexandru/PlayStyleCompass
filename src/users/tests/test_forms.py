import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from unittest.mock import patch, Mock
from django_recaptcha.fields import ReCaptchaField

from users.forms import *
from users.models import *


User = get_user_model()



class CustomAuthenticationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123"
        )

    def test_valid_authentication(self):
        form = CustomAuthenticationForm(
            data={"username": "testuser", "password": "strongpassword123"}
        )
        self.assertTrue(form.is_valid())

    def test_invalid_authentication(self):
        form = CustomAuthenticationForm(
            data={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn(
            "Incorrect username or password", form.errors["__all__"][0]
        )


class CustomRegistrationFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "profile_name": "UserNick",
            "username": "user123",
            "email": "user@example.com",
            "password1": "securePass123!",
            "password2": "securePass123!",
            "captcha": "PASSED",
        }

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_valid_registration(self, mock_validate):
        mock_validate.return_value = None
        form = CustomRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "user123")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_username_too_short(self, mock_validate):
        mock_validate.return_value = None
        data = self.valid_data.copy()
        data["username"] = "ab"
        form = CustomRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_invalid_profile_name(self, mock_validate):
        mock_validate.return_value = None
        data = self.valid_data.copy()
        data["profile_name"] = "!!badname"
        form = CustomRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("profile_name", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_passwords_do_not_match(self, mock_validate):
        mock_validate.return_value = None
        data = self.valid_data.copy()
        data["password2"] = "differentPass!"
        form = CustomRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_duplicate_email(self, mock_validate):
        mock_validate.return_value = None
        User.objects.create_user(username="user1", email="user@example.com", password="test1234")
        form = CustomRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_duplicate_username(self, mock_validate):
        mock_validate.return_value = None
        User.objects.create_user(username="user123", email="another@example.com", password="test1234")
        form = CustomRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_duplicate_profile_name(self, mock_validate):
        mock_validate.return_value = None
        user = User.objects.create_user(username="anotheruser", password="test1234")
        user.userprofile.profile_name = "UserNick"
        user.userprofile.save()
        form = CustomRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("profile_name", form.errors)


if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_forms"])
    sys.exit(bool(failures))
