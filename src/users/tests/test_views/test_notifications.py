from .base import *
import json


class MarkNotificationAsReadViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="u1@example.com", password="pass1234"
        )
        self.url_single = lambda notif_id: reverse(
            "users:mark_notification_as_read", args=[notif_id]
        )
        self.url_all = reverse("users:mark_notification_as_read")

    def test_mark_single_notification_as_read(self):
        notif = Notification.objects.create(user=self.user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        response = self.client.post(self.url_single(notif.id), secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_notifications_as_read(self):
        notif1 = Notification.objects.create(user=self.user, is_read=False)
        notif2 = Notification.objects.create(user=self.user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        response = self.client.post(self.url_all, secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        notif1.refresh_from_db()
        notif2.refresh_from_db()
        self.assertTrue(notif1.is_read)
        self.assertTrue(notif2.is_read)

    def test_invalid_method(self):
        self.client.login(username="user1", password="pass1234")
        notif = Notification.objects.create(user=self.user, is_read=False)

        response = self.client.get(self.url_single(notif.id), secure=True)

        self.assertEqual(response.status_code, 405)

    def test_mark_notification_not_owned_by_user(self):
        other_user = User.objects.create_user(
            username="user2", email="u2@example.com", password="pass1234"
        )
        notif = Notification.objects.create(user=other_user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        with self.assertRaises(Notification.DoesNotExist):
            self.client.post(self.url_single(notif.id), secure=True)

    def test_unauthenticated_access(self):
        notif = Notification.objects.create(user=self.user, is_read=False)
        response = self.client.post(self.url_single(notif.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteNotificationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="u1@example.com", password="pass1234"
        )
        self.url_single = lambda notif_id: reverse(
            "users:delete_notification", args=[notif_id]
        )
        self.url_all = reverse("users:delete_notification")

    def test_delete_single_notification(self):
        notif = Notification.objects.create(user=self.user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        response = self.client.post(self.url_single(notif.id), secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertFalse(Notification.objects.filter(id=notif.id).exists())

    def test_delete_all_notifications(self):
        notif1 = Notification.objects.create(user=self.user, is_read=False)
        notif2 = Notification.objects.create(user=self.user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        response = self.client.post(self.url_all, secure=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)

    def test_invalid_method(self):
        self.client.login(username="user1", password="pass1234")
        notif = Notification.objects.create(user=self.user, is_read=False)
        response = self.client.get(self.url_single(notif.id), secure=True)
        self.assertEqual(response.status_code, 405)

    def test_delete_notification_not_owned_by_user(self):
        other_user = User.objects.create_user(
            username="user2", email="u2@example.com", password="pass1234"
        )
        notif = Notification.objects.create(user=other_user, is_read=False)
        self.client.login(username="user1", password="pass1234")

        with self.assertRaises(Notification.DoesNotExist):
            self.client.post(self.url_single(notif.id), secure=True)

    def test_unauthenticated_access(self):
        notif = Notification.objects.create(user=self.user, is_read=False)
        response = self.client.post(self.url_single(notif.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class NotificationSettingsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="u1@example.com", password="pass1234"
        )
        self.url = reverse("users:notification_settings")

    def test_get_notification_settings_authenticated(self):
        self.client.login(username="user1", password="pass1234")

        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_related/notification_settings.html")
        self.assertIsInstance(response.context["form"], NotificationSettingsForm)

    def test_post_valid_data(self):
        self.client.login(username="user1", password="pass1234")
        profile = self.user.userprofile

        data = {
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

        response = self.client.post(self.url, data, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response.url)

        profile.refresh_from_db()
        for field, value in data.items():
            self.assertEqual(getattr(profile, field), value)

    def test_unauthenticated_access(self):
        response = self.client.get(self.url, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)




if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_notifications"])
    sys.exit(bool(failures))



