from django.conf import settings
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock, AsyncMock

from users.models import UserProfile, Notification
from playstyle_compass.models import UserPreferences
from users.signals import get_last_online


class CreateUserProfileSignalTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username="testuser", password="pass")
        profile = UserProfile.objects.get(user=user)
        self.assertTrue(profile.profile_name.startswith("Player_"))
        self.assertEqual(
            profile.profile_picture,
            "profile_pictures/default_pfp/default_profile_picture.png",
        )

    def test_unique_profile_name_if_conflict(self):
        u1 = User.objects.create_user("u1")
        u1.userprofile.profile_name = "Player_1234"
        u1.userprofile.save()

        u2 = User.objects.create_user("u2")
        self.assertNotEqual(u2.userprofile.profile_name, "Player_1234")


class CreateUserModelsSignalTest(TestCase):
    def test_user_preferences_created(self):
        user = User.objects.create_user(username="normal", password="pass")
        prefs = UserPreferences.objects.get(user=user)
        self.assertIn(prefs.quiz_recommendations, [[], "[]"])

    def test_superuser_gets_admin_profile_name(self):
        superuser = User.objects.create_superuser("admin", "a@a.com", "pass")
        profile = superuser.userprofile
        self.assertTrue(profile.profile_name in ["admin", profile.profile_name])


class NotificationSignalTest(TestCase):
    @patch("users.signals.get_channel_layer")
    def test_notification_triggers_group_send(self, mock_get_layer):
        user = User.objects.create_user("notif", password="pass")

        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer

        notif = Notification.objects.create(
            user=user,
            message="Hello",
            message_ro="Salut",
            is_read=False,
            is_active=True,
            delivered=False,
            notification_type="info",
        )

        mock_layer.group_send.assert_awaited_once()


class UserStatusSignalTest(TestCase):
    @patch("users.signals.get_channel_layer")
    def test_user_logged_in_sets_status_true(self, mock_get_layer):
        user = User.objects.create_user("online", password="pass")

        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer

        from users.signals import update_user_online_status

        update_user_online_status(sender=User, request=None, user=user)

        mock_layer.group_send.assert_awaited_once()
        args, kwargs = mock_layer.group_send.await_args
        self.assertEqual(args[0], f"user_status_{user.id}")
        self.assertTrue(args[1]["status"])

    @patch("users.signals.get_channel_layer")
    def test_user_logged_out_sets_status_false(self, mock_get_layer):
        user = User.objects.create_user("offline", password="pass")

        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer

        from users.signals import update_user_offline_status

        update_user_offline_status(sender=User, request=None, user=user)

        mock_layer.group_send.assert_awaited_once()
        args, kwargs = mock_layer.group_send.await_args
        self.assertEqual(args[0], f"user_status_{user.id}")
        self.assertFalse(args[1]["status"])


class GetLastOnlineTest(TestCase):
    def test_returns_formatted_datetime_with_timezone(self):
        user = User.objects.create_user("tzuser", password="pass")
        profile = user.userprofile
        profile.timezone = "Europe/Berlin"
        profile.last_online = timezone.now()
        profile.save()

        formatted = get_last_online(profile)
        self.assertIsInstance(formatted, str)
        self.assertIn("202", formatted)

    def test_returns_none_if_no_last_online(self):
        user = User.objects.create_user("empty", password="pass")
        profile = user.userprofile
        profile.timezone = "Europe/Berlin"
        profile.last_online = None
        profile.save()

        self.assertIsNone(get_last_online(profile))

    def test_returns_none_if_no_timezone(self):
        user = User.objects.create_user("no_tz", password="pass")
        profile = user.userprofile
        profile.last_online = timezone.now()
        profile.timezone = ""
        profile.save()

        self.assertIsNone(get_last_online(profile))
