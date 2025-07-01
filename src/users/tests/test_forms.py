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


class DeleteAccountFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')

    def test_valid_password(self):
        form = DeleteAccountForm(data={"password": "testpass123"})
        self.assertTrue(form.is_valid())

    def test_empty_password(self):
        form = DeleteAccountForm(data={"password": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_invalid_password_format(self):
        # Since the form doesn't validate password correctness because that happens elsewhere this still passes
        form = DeleteAccountForm(data={"password": "wrongpass"})
        self.assertTrue(form.is_valid())


class EmailChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass456"
        )

    def test_valid_email_change(self):
        form = EmailChangeForm(
            data={
                "current_password": "testpass123",
                "new_email": "new@example.com",
                "confirm_email": "new@example.com",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_invalid_current_password(self):
        form = EmailChangeForm(
            data={
                "current_password": "wrongpass",
                "new_email": "new@example.com",
                "confirm_email": "new@example.com",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("current_password", form.errors)

    def test_duplicate_email(self):
        form = EmailChangeForm(
            data={
                "current_password": "testpass123",
                "new_email": "other@example.com",
                "confirm_email": "other@example.com",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_email", form.errors)

    def test_same_as_current_email(self):
        form = EmailChangeForm(
            data={
                "current_password": "testpass123",
                "new_email": "tester@example.com",
                "confirm_email": "tester@example.com",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_email", form.errors)

    def test_mismatched_emails(self):
        form = EmailChangeForm(
            data={
                "current_password": "testpass123",
                "new_email": "new@example.com",
                "confirm_email": "different@example.com",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_email", form.errors)


class CustomPasswordChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPassword1!")

    def test_valid_password_change(self):
        form = CustomPasswordChangeForm(
            data={
                "old_password": "TestPassword1!",
                "new_password1": "Newtestpassword12!",
                "new_password2": "Newtestpassword12!",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_invalid_password_change(self):
        form = CustomPasswordChangeForm(
            data={
                "old_password": "TestPassword1!Wrong",
                "new_password1": "Newtestpassword12!",
                "new_password2": "Newtestpassword12!",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("old_password", form.errors)

    def test_mismatched_passwords(self):
        form = CustomPasswordChangeForm(
            data={
                "old_password": "TestPassword1!",
                "new_password1": "Newtestpassword12!",
                "new_password2": "Newtestpassword12!Different",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_password2", form.errors)

    def test_weak_new_password(self):
        form = CustomPasswordChangeForm(
            data={
                "old_password": "TestPassword1!",
                "new_password1": "123",
                "new_password2": "123",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_password1", form.errors)

    def test_empty_fields(self):
        form = CustomPasswordChangeForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("old_password", form.errors)
        self.assertIn("new_password1", form.errors)
        self.assertIn("new_password2", form.errors)

if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_forms"])
    sys.exit(bool(failures))
