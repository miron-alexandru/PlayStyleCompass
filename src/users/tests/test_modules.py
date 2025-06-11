import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.playstyle_manager.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import *

User = get_user_model()

class ContactMessageModelTest(TestCase):
    def setUp(self):
        self.message = ContactMessage.objects.create(
            name="Test User",
            email="testemail@example.com",
            subject="Test Subject",
            message="This is a test message."
        )

    def test_contact_message_creation(self):
        self.assertEqual(self.message.name, "Test User")
        self.assertEqual(self.message.email, "testemail@example.com")
        self.assertEqual(self.message.subject, "Test Subject")
        self.assertEqual(self.message.message, "This is a test message.")
        self.assertIsNotNone(self.message.timestamp)

    def test_formatted_timestamp(self):
        formatted = self.message.formatted_timestamp()
        self.assertIsInstance(formatted, str)
        self.assertIn(",", formatted)

class FriendListModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.user3 = User.objects.create_user(username="user3", password="pass")

        self.friend_list1 = FriendList.objects.create(user=self.user1)
        self.friend_list2 = FriendList.objects.create(user=self.user2)
        self.friend_list3 = FriendList.objects.create(user=self.user3)

    def test_str_representation(self):
        self.assertEqual(str(self.friend_list1), "user1")

    def test_add_friend(self):
        self.friend_list1.add_friend(self.user2)
        self.assertTrue(self.friend_list1.is_friend(self.user2))
        self.assertIn(self.user2, self.friend_list1.friends.all())

        # Should not add duplicate
        self.friend_list1.add_friend(self.user2)
        self.assertEqual(self.friend_list1.friends.count(), 1)

    def test_remove_friend(self):
        self.friend_list1.add_friend(self.user2)
        self.friend_list1.remove_friend(self.user2)
        self.assertFalse(self.friend_list1.is_friend(self.user2))

    def test_unfriend(self):
        self.friend_list1.add_friend(self.user2)
        self.friend_list2.add_friend(self.user1)

        self.friend_list1.unfriend(self.user2)

        self.assertFalse(self.friend_list1.is_friend(self.user2))
        self.assertFalse(self.friend_list2.is_friend(self.user1))

    def test_is_friend(self):
        self.friend_list1.add_friend(self.user3)
        self.assertTrue(self.friend_list1.is_friend(self.user3))
        self.assertFalse(self.friend_list1.is_friend(self.user2))


class FriendRequestModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass123")
        self.receiver = User.objects.create_user(username="receiver", password="pass123")
        self.sender_friend_list = FriendList.objects.create(user=self.sender)
        self.receiver_friend_list = FriendList.objects.create(user=self.receiver)
        self.request = FriendRequest.objects.create(sender=self.sender, receiver=self.receiver)

    def test_str_representation(self):
        self.assertEqual(str(self.request), self.sender.username)

    def test_accept_request(self):
        self.request.accept()
        self.assertTrue(self.sender in self.receiver_friend_list.friends.all())
        self.assertTrue(self.receiver in self.sender_friend_list.friends.all())

    def test_decline_request(self):
        self.request.decline()
        self.assertFalse(self.request.is_active)

    def test_cancel_request(self):
        self.request.cancel()
        self.assertFalse(self.request.is_active)

    def test_activate_request(self):
        self.request.is_active = False
        self.request.activate()
        self.assertTrue(self.request.is_active)

    def test_delete_request(self):
        self.request.delete()
        self.assertFalse(FriendRequest.objects.filter(id=self.request.id).exists())


class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass123")
        self.receiver = User.objects.create_user(username="receiver", password="pass123")
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            title="Hello",
            message="This is a test message.",
        )

    def test_message_creation(self):
        self.assertEqual(self.message.sender, self.sender)
        self.assertEqual(self.message.receiver, self.receiver)
        self.assertEqual(self.message.title, "Hello")
        self.assertEqual(self.message.message, "This is a test message.")
        self.assertFalse(self.message.is_deleted_by_sender)
        self.assertFalse(self.message.is_deleted_by_receiver)
        self.assertIsNotNone(self.message.timestamp)

    def test_str_representation(self):
        expected = f"Message from {self.sender} to {self.receiver}"
        self.assertEqual(str(self.message), expected)


if __name__ == "__main__":
    import django
    import os
    import sys
    from django.conf import settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playstyle_manager.settings")
    django.setup()

    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users"])
    sys.exit(bool(failures))
