from .base import *

from django.test import Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.files.storage import default_storage


@override_settings(MEDIA_ROOT="/tmp/django_test_media/")
class CreateMessageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient", password="pass")

        self.url = reverse("users:create_message")
        self.client.login(username="sender", password="pass")

        self.sender.userprofile.profile_name = "SenderProfile"
        self.sender.userprofile.save()
        self.recipient.userprofile.profile_name = "RecipientProfile"
        self.recipient.userprofile.save()

        session = self.client.session
        session["user_id"] = self.sender.id
        session["recipient_id"] = self.recipient.id
        session.save()

        cache.clear()

    def test_invalid_request_method(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn("Invalid request method", response.json()["error"])

    def test_missing_session_data(self):
        session = self.client.session
        del session["user_id"]
        session.save()
        response = self.client.post(self.url, {"content": "Hi"}, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.json()["error"])

    def test_recipient_blocked_sender(self):
        self.recipient.userprofile.blocked_users.add(self.sender)
        response = self.client.post(self.url, {"content": "Hello"}, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn("RecipientProfile is no longer available.", response.json()["error"])

    def test_sender_blocked_recipient(self):
        self.sender.userprofile.blocked_users.add(self.recipient)
        response = self.client.post(self.url, {"content": "Hello"}, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn("RecipientProfile is in your block list.", response.json()["error"])

    def test_empty_message_and_no_file(self):
        response = self.client.post(self.url, {}, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must write something", response.json()["error"])

    def test_file_too_large(self):
        file = SimpleUploadedFile("bigfile.txt", b"x" * (26 * 1024 * 1024))
        response = self.client.post(self.url, {"file": file, "content": ""}, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("File size exceeds the limit", response.json()["error"])

    @patch("users.views.default_storage.save")
    @patch("users.views.default_storage.url")
    def test_file_upload_success(self, mock_url, mock_save):
        mock_save.return_value = "chat_files/test.txt"
        mock_url.return_value = "/media/chat_files/test.txt"
        file = SimpleUploadedFile("test.txt", b"hello")

        response = self.client.post(self.url, {"file": file, "content": ""}, secure=True)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "Message created")
        self.assertTrue(ChatMessage.objects.filter(id=data["id"]).exists())
        msg = ChatMessage.objects.get(id=data["id"])
        self.assertEqual(msg.file, "/media/chat_files/test.txt")

    def test_successful_message_creation(self):
        response = self.client.post(self.url, {"content": "Hello"}, secure=True)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "Message created")
        self.assertTrue(ChatMessage.objects.filter(id=data["id"]).exists())
        msg = ChatMessage.objects.get(id=data["id"])
        self.assertEqual(msg.content, "Hello")
        self.assertEqual(msg.sender, self.sender)
        self.assertEqual(msg.recipient, self.recipient)


class EditMessageViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.message = ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other,
            content="hello",
        )
        self.url = lambda mid: reverse("users:edit_message", args=[mid])

    def login(self):
        self.client.login(username="testuser", password="pass")
        session = self.client.session
        session["user_id"] = self.user.id
        session.save()

    def test_post_edit_success(self):
        self.login()
        response = self.client.post(
            self.url(self.message.id), {"content": "updated"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.content, "updated")
        self.assertTrue(self.message.edited)

    def test_get_invalid_method(self):
        self.login()
        response = self.client.get(self.url(self.message.id), secure=True)
        self.assertEqual(response.status_code, 405)

    def test_no_session_user_id(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.post(
            self.url(self.message.id), {"content": "updated"}, secure=True
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_not_owner(self):
        self.login()
        response = self.client.post(
            self.url(self.message.id), {"content": "ok"}, secure=True
        )
        self.assertEqual(response.status_code, 200)

        self.client.login(username="other", password="pass")
        session = self.client.session
        session["user_id"] = self.other.id
        session.save()

        response = self.client.post(
            self.url(self.message.id), {"content": "not allowed"}, secure=True
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_time_limit_exceeded(self):
        self.login()
        self.message.created_at = timezone.now() - timedelta(minutes=3)
        self.message.save()
        response = self.client.post(
            self.url(self.message.id), {"content": "too late"}, secure=True
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("time limit", response.json()["error"])

    def test_empty_content(self):
        self.login()
        response = self.client.post(
            self.url(self.message.id), {"content": ""}, secure=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("write something", response.json()["error"])


class ChatViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.url = lambda rid: reverse("users:chat", args=[rid])

    def test_chat_authenticated(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(self.other.id), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/chat.html")
        self.assertEqual(response.context["recipient"], self.other)

        session = self.client.session
        self.assertEqual(session["user_id"], self.user.id)
        self.assertEqual(session["recipient_id"], self.other.id)

    def test_chat_unauthenticated(self):
        response = self.client.get(self.url(self.other.id), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_chat_invalid_recipient(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(self.url(9999), secure=True)
        self.assertEqual(response.status_code, 404)


class ChatListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")
        self.url = reverse("users:chat_list")

        self.client.login(username="user1", password="pass")

    def test_chat_messages(self):
        now = timezone.now()
        ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other,
            content="Hello there",
            created_at=now - timedelta(minutes=1),
        )
        ChatMessage.objects.create(
            sender=self.other,
            recipient=self.user,
            content="Hi back",
            created_at=now,
        )

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/chat_list.html")
        chat_info = response.context["chat_info"]
        self.assertEqual(len(chat_info), 1)
        self.assertEqual(chat_info[0]["user"], self.other)
        self.assertIn(chat_info[0]["latest_message"].split(" ")[0], ["Hello", "Hi"])

    def test_no_messages(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/chat_list.html")
        chat_info = response.context["chat_info"]
        self.assertEqual(len(chat_info), 0)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)


class DeleteChatMessagesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")

        self.chat1 = ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other,
            content="Message 1"
        )
        self.chat2 = ChatMessage.objects.create(
            sender=self.other,
            recipient=self.user,
            content="Message 2"
        )

        self.url = reverse("users:delete_chat_messages", args=[self.other.id])
        self.client.login(username="user1", password="pass")

    def test_authenticated_user_hides_messages(self):
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        self.chat1.refresh_from_db()
        self.chat2.refresh_from_db()
        self.assertTrue(self.chat1.sender_hidden)
        self.assertTrue(self.chat2.recipient_hidden)

    def test_redirect_for_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_nonexistent_recipient_returns_404(self):
        invalid_url = reverse("users:delete_chat_messages", args=[9999])
        response = self.client.post(invalid_url, secure=True)
        self.assertEqual(response.status_code, 404)


class TogglePinMessageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")

        self.message = ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other,
            content="Important message"
        )

        self.url = reverse("users:toggle_pin_message", args=[self.message.id])
        self.client.login(username="user1", password="pass")

    def test_pin(self):
        res = self.client.post(self.url, secure=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["action"], "pinned")
        self.assertIn(self.user, self.message.pinned_by.all())

    def test_unpin(self):
        self.message.pinned_by.add(self.user)
        res = self.client.post(self.url, secure=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["action"], "unpinned")
        self.assertNotIn(self.user, self.message.pinned_by.all())

    def test_needs_login(self):
        self.client.logout()
        res = self.client.post(self.url, secure=True)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/users/login/", res.url)

    def test_404_on_missing(self):
        bad_url = reverse("users:toggle_pin_message", args=[9999])
        res = self.client.post(bad_url, secure=True)
        self.assertEqual(res.status_code, 404)


class LoadPinnedMessagesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")

        self.msg_user = ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other,
            content="From user"
        )
        self.msg_other = ChatMessage.objects.create(
            sender=self.other,
            recipient=self.user,
            content="From other"
        )

        self.url = reverse("users:load_pinned_messages", args=[self.other.id])
        self.client.login(username="user1", password="pass")

    def test_loads_pinned(self):
        self.msg_user.pinned_by.add(self.user)
        self.msg_other.pinned_by.add(self.user)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 2)

        ids = [m["id"] for m in data]
        self.assertIn(self.msg_user.id, ids)
        self.assertIn(self.msg_other.id, ids)

    def test_labels_you(self):
        self.msg_user.pinned_by.add(self.user)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data[0]["sender__userprofile__profile_name"], "You")

    def test_empty(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_needs_login(self):
        self.client.logout()
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_bad_recipient(self):
        url = reverse("users:load_pinned_messages", args=[9999])
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 404)


class GetChatMessagesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")

        self.user.userprofile.profile_name = "User1"
        self.user.userprofile.profile_picture = "pic1.png"
        self.user.userprofile.save()

        self.other.userprofile.profile_name = "User2"
        self.other.userprofile.profile_picture = "pic2.png"
        self.other.userprofile.save()

        self.m1 = GlobalChatMessage.objects.create(sender=self.user, content="Hello")
        self.m2 = GlobalChatMessage.objects.create(sender=self.other, content="Hi")

        self.url = reverse("users:get_chat_messages")
        self.client.login(username="user1", password="pass")

    def test_list(self):
        res = self.client.get(self.url, {"offset": 0, "limit": 10}, secure=True)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["message"], "Hi")
        self.assertEqual(data[1]["message"], "Hello")

    def test_pagination(self):
        res = self.client.get(self.url, {"offset": 0, "limit": 1}, secure=True)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["message"], "Hi")

    def test_needs_login(self):
        self.client.logout()
        res = self.client.get(self.url, secure=True)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/users/login/", res.url)


class GetPrivateChatMessagesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other = User.objects.create_user(username="user2", password="pass")

        self.user.userprofile.profile_picture = "pic1.png"
        self.user.userprofile.save()
        self.other.userprofile.profile_picture = "pic2.png"
        self.other.userprofile.save()

        self.m1 = ChatMessage.objects.create(
            sender=self.user, recipient=self.other, content="Hello"
        )
        self.m2 = ChatMessage.objects.create(
            sender=self.other, recipient=self.user, content="Hi"
        )

        self.url = lambda rid, **params: reverse(
            "users:get_private_chat_messages", args=[rid]
        ) + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")

        self.client.login(username="user1", password="pass")

    def test_list(self):
        res = self.client.get(self.url(self.other.id, offset=0, limit=10), secure=True)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["message"], "Hi")
        self.assertEqual(data[1]["message"], "Hello")

    def test_pagination(self):
        res = self.client.get(self.url(self.other.id, offset=0, limit=1), secure=True)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["message"], "Hi")

    def test_hidden_sender(self):
        self.m1.sender_hidden = True
        self.m1.save()
        res = self.client.get(self.url(self.other.id), secure=True)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["message"], "Hi")

    def test_hidden_recipient(self):
        self.m2.recipient_hidden = True
        self.m2.save()
        res = self.client.get(self.url(self.other.id), secure=True)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["message"], "Hello")

    def test_pinned_status(self):
        self.m1.pinned_by.add(self.user)
        res = self.client.get(self.url(self.other.id), secure=True)
        data = res.json()
        message = [m for m in data if m["id"] == self.m1.id][0]
        self.assertTrue(message["is_pinned"])

    def test_recipient_not_found(self):
        res = self.client.get(self.url(9999), secure=True)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["error"], "Recipient not found.")

    def test_needs_login(self):
        self.client.logout()
        res = self.client.get(self.url(self.other.id), secure=True)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/users/login/", res.url)

class CreateGlobalChatMessageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.url = reverse("users:create_global_chat_message")
        self.client.login(username="user1", password="pass")

    def test_create_message_ok(self):
        response = self.client.post(self.url, {"content": "hello"}, secure=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "Message created")
        self.assertTrue(GlobalChatMessage.objects.filter(sender=self.user, content="hello").exists())

    def test_missing_content(self):
        response = self.client.post(self.url, {}, secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_invalid_method(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn("Invalid request method", response.json()["error"])

    def test_rate_limit(self):
        cache_key = f"global_message_count_{self.user.username}"
        cache.delete(cache_key)  # reset cache before test

        for _ in range(8):
            self.client.post(self.url, {"content": "spam"}, secure=True)

        response = self.client.post(self.url, {"content": "too fast"}, secure=True)
        self.assertEqual(response.status_code, 429)
        self.assertIn("rate_limited", response.json())
        self.assertTrue(response.json()["rate_limited"])

    def test_redirect_for_anonymous(self):
        self.client.logout()
        response = self.client.post(self.url, {"content": "hello"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

if __name__ == "__main__":
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users.tests.test_views.test_chat"])
    sys.exit(bool(failures))
