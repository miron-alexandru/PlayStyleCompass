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
from django.utils import timezone
from datetime import timedelta
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


class QuizQuestionModelTest(TestCase):
    def setUp(self):
        self.question = QuizQuestion.objects.create(
            name="Visual Novel",
            question_text="How do you feel about visual novels?",
            option1="I'm okay with them if they have engaging narratives and choices.",
            option2="I'm not particularly interested in visual novels."
        )

    def test_str_representation(self):
        expected = f"Quiz question: Visual Novel"
        self.assertEqual(str(self.question), expected)

    def test_question_creation(self):
        self.assertEqual(self.question.name, "Visual Novel")
        self.assertEqual(self.question.question_text, "How do you feel about visual novels?")
        self.assertEqual(self.question.option1, "I'm okay with them if they have engaging narratives and choices.")
        self.assertIsNotNone(self.question.option3)

class QuizUserResponseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.question = QuizQuestion.objects.create(
            name="Visual Novel",
            question_text="How do you feel about visual novels?",
            option1="I'm okay with them if they have engaging narratives and choices.",
            option2="I'm not particularly interested in visual novels."
        )

        self.quiz_response = QuizUserResponse.objects.create(
            user=self.user,
            question=self.question,
            response_text="I'm not particularly interested in visual novels.",
            )

    def test_str_representation(self):
        expected = f"Response from {self.user} for the question Visual Novel"
        self.assertEqual(str(self.quiz_response), expected)

    def test_question_response_creation(self):
        self.assertEqual(self.quiz_response.user, self.user)
        self.assertEqual(self.quiz_response.question, self.question)
        self.assertEqual(self.quiz_response.response_text, self.question.option2)
        self.assertIsNotNone(self.quiz_response.updated_at)

    def test_updated_at_auto_updates_on_save(self):
        response = QuizUserResponse.objects.create(
            user=self.user,
            question=self.question,
            response_text="Initial"
        )
        old_timestamp = response.updated_at

        response.response_text = "Updated"
        response.save()

        self.assertGreater(response.updated_at, old_timestamp)
        self.assertAlmostEqual(
            (timezone.now() - response.updated_at).total_seconds(), 0, delta=5
        )


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass123")
        self.recipient = User.objects.create_user(username="recipient", password="pass123")
        self.message = ChatMessage.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            content="Hello, test chat message.",
            file="https://example.com/file.pdf",
            file_size=1024
        )

    def test_chat_message_creation(self):
        self.assertEqual(self.message.sender, self.sender)
        self.assertEqual(self.message.recipient, self.recipient)
        self.assertEqual(self.message.content, "Hello, test chat message.")
        self.assertEqual(self.message.file, "https://example.com/file.pdf")
        self.assertEqual(self.message.file_size, 1024)
        self.assertFalse(self.message.sender_hidden)
        self.assertFalse(self.message.recipient_hidden)
        self.assertFalse(self.message.edited)

    def test_str_representation(self):
        expected = f"{self.sender.username} to {self.recipient.username}: Hello, test chat mes"
        self.assertEqual(str(self.message), expected)

    def test_pinning_message(self):
        self.message.pinned_by.add(self.sender)
        self.assertIn(self.sender, self.message.pinned_by.all())


class FollowModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.follow = Follow.objects.create(follower=self.user1, followed=self.user2)

    def test_follow_creation(self):
        self.assertEqual(self.follow.follower, self.user1)
        self.assertEqual(self.follow.followed, self.user2)

    def test_str_representation(self):
        self.assertEqual(str(self.follow), f"{self.user1} follows {self.user2}")

    def test_follow_unique_constraint(self):
        with self.assertRaises(Exception):
            Follow.objects.create(follower=self.user1, followed=self.user2)


class GlobalChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="globaluser", password="pass123")
        self.global_msg = GlobalChatMessage.objects.create(
            sender=self.user,
            content="This is a global chat message."
        )

    def test_global_chat_message_creation(self):
        self.assertEqual(self.global_msg.sender, self.user)
        self.assertEqual(self.global_msg.content, "This is a global chat message.")
        self.assertIsNotNone(self.global_msg.created_at)

    def test_str_representation(self):
        self.assertEqual(str(self.global_msg), "globaluser: This is a global chat message.")


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
