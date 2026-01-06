import os

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from unittest.mock import patch

from users.forms import *
from users.models import *

import tempfile
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.files.storage import default_storage
import shutil
from django.utils.translation import gettext as _


User = get_user_model()
MEDIA_ROOT = tempfile.mkdtemp()


class CustomAuthenticationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="strongpassword123"
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
        self.assertIn("Incorrect username or password", form.errors["__all__"][0])


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
        User.objects.create_user(
            username="user1", email="user@example.com", password="test1234"
        )
        form = CustomRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_duplicate_username(self, mock_validate):
        mock_validate.return_value = None
        User.objects.create_user(
            username="user123", email="another@example.com", password="test1234"
        )
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
        self.user = User.objects.create_user(username="tester", password="testpass123")

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
        self.user = User.objects.create_user(
            username="testuser", password="TestPassword1!"
        )

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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ProfilePictureFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = self.user.userprofile

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def generate_test_image(self, name="test.png", size=(500, 500), color=(255, 0, 0)):
        """Generate a dummy image."""
        image = Image.new("RGB", size, color)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.read(), content_type="image/png")

    def test_profile_picture_upload_and_resize(self):
        image = self.generate_test_image()
        form = ProfilePictureForm(
            data={}, files={"profile_picture": image}, instance=self.profile
        )
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertTrue(instance.profile_picture)
        self.assertTrue(os.path.exists(instance.profile_picture.path))

        with Image.open(instance.profile_picture.path) as img:
            self.assertLessEqual(img.width, 250)
            self.assertLessEqual(img.height, 250)

        # Filename check
        expected_prefix = f"profile_picture_{timezone.now().strftime('%Y.%m.%d.%H')}"
        self.assertIn(expected_prefix, instance.profile_picture.name)

    def test_old_profile_picture_is_deleted(self):
        old_image = self.generate_test_image(name="old.png")
        self.profile.profile_picture.save("old.png", old_image, save=True)

        old_path = self.profile.profile_picture.path
        self.assertTrue(os.path.exists(old_path))

        new_image = self.generate_test_image(name="new.png")
        form = ProfilePictureForm(
            data={}, files={"profile_picture": new_image}, instance=self.profile
        )
        self.assertTrue(form.is_valid())
        form.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(self.profile.profile_picture)

    @patch("users.forms.ProfilePictureForm.resize_image")
    def test_no_image_uploaded_does_not_change_picture(self, mock_resize):
        old_image = self.generate_test_image(name="original.png")
        self.profile.profile_picture.save("original.png", old_image, save=True)

        form = ProfilePictureForm(data={}, files={}, instance=self.profile)
        self.assertTrue(form.is_valid())
        instance = form.save()

        mock_resize.assert_called_once()
        self.assertEqual(instance.profile_picture.name, "profile_pictures/original.png")


class ContactFormTest(TestCase):
    def test_valid_data(self):
        form = ContactForm(
            data={
                "name": "Test Name",
                "email": "Test@example.com",
                "subject": "Hello",
                "message": "This is a test message.",
            }
        )
        self.assertTrue(form.is_valid())

    def test_missing_required_fields(self):
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("subject", form.errors)
        self.assertIn("message", form.errors)


class ProfileUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.profile = self.user.userprofile
        self.profile.profile_name = "OldName"

        self.other_user = User.objects.create_user(
            username="otheruser", password="pass1234"
        )
        self.other_profile = self.other_user.userprofile
        self.other_profile.profile_name = "OtherName"
        self.other_profile.save()

    def test_valid_profile_name(self):
        form = ProfileUpdateForm(
            data={"profile_name": "NewName"},
            instance=self.profile,
        )
        self.assertTrue(form.is_valid())

    def test_profile_name_invalid_characters(self):
        form = ProfileUpdateForm(
            data={"profile_name": "Invalid*Name!"},
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            _("Profile name should only contain letters and numbers."),
            form.errors["profile_name"],
        )

    def test_profile_name_too_short(self):
        form = ProfileUpdateForm(
            data={"profile_name": "ab"},
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            _("Profile name should be at least three characters long."),
            form.errors["profile_name"],
        )

    def test_profile_name_same_as_existing(self):
        form = ProfileUpdateForm(
            data={"profile_name": "OldName"},
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            _("The new profile name is the same as the existing one."),
            form.errors["profile_name"],
        )

    def test_profile_name_duplicate(self):
        form = ProfileUpdateForm(
            data={"profile_name": "OtherName"},
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            _("This profile name is already in use."),
            form.errors["profile_name"],
        )


class MessageFormTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass123")
        self.receiver = User.objects.create_user(
            username="receiver", password="pass123"
        )

    def test_valid_message_form(self):
        form_data = {
            "title": "Hello",
            "message": "Just checking in!",
        }
        form = MessageForm(data=form_data)
        self.assertTrue(form.is_valid())

        message = form.save(commit=False)
        message.sender = self.sender
        message.receiver = self.receiver
        message.save()

        self.assertEqual(message.title, "Hello")
        self.assertEqual(message.message, "Just checking in!")
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)

    def test_invalid_message_form_empty_fields(self):
        form = MessageForm(data={"title": "", "message": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("message", form.errors)


class QuizFormTest(TestCase):
    def setUp(self):
        self.question1 = QuizQuestion.objects.create(
            name="Q1",
            question_text="What is 2 + 2?",
            option1="3",
            option2="4",
            option3="5",
            option4="6",
        )
        self.question2 = QuizQuestion.objects.create(
            name="Q2",
            question_text="What is the capital of France?",
            option1="Berlin",
            option2="Madrid",
            option3="Paris",
            option4="Rome",
        )

    def test_valid_quiz_submission(self):
        form_data = {
            f"question_{self.question1.id}": "option2",
            f"question_{self.question2.id}": "option3",
        }
        form = QuizForm(data=form_data, questions=[self.question1, self.question2])
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data[f"question_{self.question1.id}"], "option2")
        self.assertEqual(form.cleaned_data[f"question_{self.question2.id}"], "option3")

    def test_invalid_quiz_submission_missing_answer(self):
        form_data = {
            f"question_{self.question1.id}": "option2",
        }
        form = QuizForm(data=form_data, questions=[self.question1, self.question2])
        self.assertFalse(form.is_valid())
        self.assertIn(f"question_{self.question2.id}", form.errors)


class NotificationSettingsFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = self.user.userprofile

    def test_all_notifications_enabled(self):
        form_data = {
            "receive_review_notifications": True,
            "receive_follow_notifications": True,
            "receive_friend_request_notifications": True,
            "receive_message_notifications": True,
            "receive_chat_message_notifications": True,
            "receive_shared_game_notifications": True,
            "receive_shared_game_list_notifications": True,
            "receive_shared_deal_notifications": True,
            "receive_shared_review_notifications": True,
        }
        form = NotificationSettingsForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

        updated_profile = form.save()
        for field in form_data:
            self.assertTrue(getattr(updated_profile, field))

    def test_all_notifications_disabled(self):
        form_data = {
            "receive_review_notifications": False,
            "receive_follow_notifications": False,
            "receive_friend_request_notifications": False,
            "receive_message_notifications": False,
            "receive_chat_message_notifications": False,
            "receive_shared_game_notifications": False,
            "receive_shared_game_list_notifications": False,
            "receive_shared_deal_notifications": False,
            "receive_shared_review_notifications": False,
        }
        form = NotificationSettingsForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

        updated_profile = form.save()
        for field in form_data:
            self.assertFalse(getattr(updated_profile, field))

    def test_partial_update_some_checked(self):
        form_data = {
            "receive_review_notifications": True,
            "receive_follow_notifications": False,
            "receive_friend_request_notifications": True,
            "receive_message_notifications": False,
            "receive_chat_message_notifications": True,
            "receive_shared_game_notifications": False,
            "receive_shared_game_list_notifications": True,
            "receive_shared_deal_notifications": False,
            "receive_shared_review_notifications": True,
        }
        form = NotificationSettingsForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

        updated_profile = form.save()
        for field, expected_value in form_data.items():
            self.assertEqual(getattr(updated_profile, field), expected_value)

    def test_form_renders_all_fields(self):
        form = NotificationSettingsForm(instance=self.profile)
        rendered = form.as_p()
        for field_name in NotificationSettingsForm.Meta.fields:
            self.assertIn(field_name, rendered)


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass")
        self.profile = self.user.userprofile  # auto-created

        self.valid_data = {
            "bio": "I love gaming!",
            "favorite_game": "The Witcher 3",
            "favorite_character": "Geralt",
            "gaming_commitment": GAMING_COMMITMENT_CHOICES[0][0],
            "main_gaming_platform": PLATFORM_CHOICES[0][0],
            "social_media": "https://x.com/testgamer",
            "gaming_setup": "RTX 4090, Dual monitors, etc.",
            "favorite_franchise": "Elder Scrolls",
            "last_finished_game": "Skyrim",
            "streaming_preferences": "Twitch",
            "current_game": "Starfield",
            "favorite_soundtrack": "Skyrim OST",
            "gaming_alias": "Dragonborn",
            "gaming_genres": [GENRE_CHOICES[0][0], GENRE_CHOICES[1][0]],
            "favorite_game_modes": [GAME_MODES_CHOICES[0][0]],
        }

    def test_valid_form_submission(self):
        form = UserProfileForm(data=self.valid_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.favorite_game, "The Witcher 3")
        self.assertIn(GENRE_CHOICES[0][0], instance.gaming_genres)
        self.assertIn(GAME_MODES_CHOICES[0][0], instance.favorite_game_modes)

    def test_invalid_too_many_genres(self):
        form_data = self.valid_data.copy()
        form_data["gaming_genres"] = [g[0] for g in GENRE_CHOICES[:4]]  # 4 genres
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn("gaming_genres", form.errors)
        self.assertEqual(
            form.errors["gaming_genres"][0], "You can only select up to 3 genres."
        )

    def test_invalid_too_many_game_modes(self):
        form_data = self.valid_data.copy()
        form_data["favorite_game_modes"] = [g[0] for g in GAME_MODES_CHOICES[:4]]
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn("favorite_game_modes", form.errors)
        self.assertEqual(
            form.errors["favorite_game_modes"][0],
            "You can only select up to 3 game modes.",
        )

    def test_invalid_social_media_url(self):
        form_data = self.valid_data.copy()
        form_data["social_media"] = "https://unknownsite.com/profile"
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn("social_media", form.errors)
        self.assertEqual(
            form.errors["social_media"][0], "Please enter a valid social media link."
        )

    def test_empty_social_media_is_valid(self):
        form_data = self.valid_data.copy()
        form_data["social_media"] = ""
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
