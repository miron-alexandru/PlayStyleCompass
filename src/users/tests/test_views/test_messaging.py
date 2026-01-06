from .base import *


class SendMessageViewTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.receiver = User.objects.create_user(username="receiver", password="pass")
        self.url = reverse("users:send_message", args=[self.receiver.id])

    def test_get_message_form_authenticated(self):
        self.client.login(username="sender", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/send_message.html")
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["receiver"],
            self.receiver.userprofile.profile_name
        )

    def test_get_message_form_requires_login(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_send_message_success(self):
        self.client.login(username="sender", password="pass")
        response = self.client.post(
            self.url,
            {"title": "Test", "message": "Hello"},
            secure=True,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Message.objects.filter(
                sender=self.sender,
                receiver=self.receiver,
                message="Hello"
            ).exists()
        )

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Message sent successfully!", messages)

    def test_send_message_sender_blocked_by_receiver(self):
        self.receiver.userprofile.blocked_users.add(self.sender)
        self.client.login(username="sender", password="pass")

        response = self.client.post(
            self.url,
            {"title": "Blocked", "message": "Hi"},
            secure=True,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(
            f"{self.receiver.userprofile.profile_name} is no longer available.",
            messages
        )

        self.assertFalse(
            Message.objects.filter(sender=self.sender, receiver=self.receiver).exists()
        )

    def test_send_message_receiver_in_sender_block_list(self):
        self.sender.userprofile.blocked_users.add(self.receiver)
        self.client.login(username="sender", password="pass")

        response = self.client.post(
            self.url,
            {"title": "Blocked", "message": "Hi"},
            secure=True,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(
            f"{self.receiver.userprofile.profile_name} is in your block list.",
            messages
        )

        self.assertFalse(
            Message.objects.filter(sender=self.sender, receiver=self.receiver).exists()
        )

    def test_invalid_form_submission(self):
        self.client.login(username="sender", password="pass")
        response = self.client.post(
            self.url,
            {"title": "", "message": ""},
            secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/send_message.html")
        self.assertFalse(
            Message.objects.filter(sender=self.sender, receiver=self.receiver).exists()
        )


class InboxViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.url = reverse("users:inbox")
        profile = UserProfile.objects.get(user=self.user)
        profile.timezone = "UTC"
        profile.save()

        now = timezone.now()
        # Received messages
        self.msg1 = Message.objects.create(
            sender=self.other,
            receiver=self.user,
            title="Msg1",
            message="Hi user",
            timestamp=now - timedelta(minutes=5),
        )
        self.msg2 = Message.objects.create(
            sender=self.other,
            receiver=self.user,
            title="Msg2",
            message="Hello again",
            timestamp=now - timedelta(minutes=2),
        )
        # Sent message
        self.msg3 = Message.objects.create(
            sender=self.user,
            receiver=self.other,
            title="Msg3",
            message="Hi other",
            timestamp=now - timedelta(minutes=1),
        )

    def test_login_required(self):
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_default_received_messages(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/inbox.html")
        messages = list(response.context["user_messages"])
        self.assertIn(self.msg1, messages)
        self.assertIn(self.msg2, messages)
        self.assertNotIn(self.msg3, messages)
        self.assertEqual(response.context["category"], "received")
        self.assertEqual(response.context["selected_sort_order"], "asc")

    def test_sent_messages_category(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?category=sent", secure=True)
        messages = list(response.context["user_messages"])
        self.assertIn(self.msg3, messages)
        self.assertNotIn(self.msg1, messages)
        self.assertEqual(response.context["category"], "sent")

    def test_invalid_category(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?category=invalid", secure=True)
        self.assertEqual(list(response.context["user_messages"]), [])

    def test_sort_order_asc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=asc", secure=True)
        timestamps = [m.timestamp for m in response.context["user_messages"]]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(response.context["selected_sort_order"], "asc")

    def test_sort_order_desc(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(self.url + "?sort_order=desc", secure=True)
        timestamps = [m.timestamp for m in response.context["user_messages"]]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
        self.assertEqual(response.context["selected_sort_order"], "desc")

    def test_deleted_messages_not_shown(self):
        self.msg1.is_deleted_by_receiver = True
        self.msg1.save()
        self.msg3.is_deleted_by_sender = True
        self.msg3.save()

        self.client.login(username="user", password="pass")

        response = self.client.get(self.url, secure=True)
        self.assertNotIn(self.msg1, response.context["user_messages"])

        response = self.client.get(self.url + "?category=sent", secure=True)
        self.assertNotIn(self.msg3, response.context["user_messages"])


class DeleteMessagesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")

        self.received_message = Message.objects.create(
            sender=self.other_user,
            receiver=self.user,
            title="Hello",
            message="Hello received",
            is_deleted_by_receiver=False,
            is_deleted_by_sender=False,
        )

        self.sent_message = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            title="Hi",
            message="Hello sent",
            is_deleted_by_receiver=False,
            is_deleted_by_sender=False,
        )

        self.url = reverse("users:delete_messages") + "?category=received&sort_order=asc"

    def test_redirect_authenticated_user(self):
        self.client.login(username="user", password="pass")
        response = self.client.post(
            self.url,
            {
                "received_messages[]": [self.received_message.id],
                "sent_messages[]": [self.sent_message.id],
            },
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:inbox"), response.url)

    def test_delete_received_message(self):
        self.client.login(username="user", password="pass")
        self.client.post(
            self.url, {"received_messages[]": [self.received_message.id]}, secure=True
        )
        self.received_message.refresh_from_db()
        self.assertTrue(self.received_message.is_deleted_by_receiver)
        # Should not affect sent message
        self.sent_message.refresh_from_db()
        self.assertFalse(self.sent_message.is_deleted_by_sender)

    def test_delete_sent_message(self):
        self.client.login(username="user", password="pass")
        self.client.post(
            self.url, {"sent_messages[]": [self.sent_message.id]}, secure=True
        )
        self.sent_message.refresh_from_db()
        self.assertTrue(self.sent_message.is_deleted_by_sender)
        # Should not affect received message
        self.received_message.refresh_from_db()
        self.assertFalse(self.received_message.is_deleted_by_receiver)

    def test_delete_both_messages(self):
        self.client.login(username="user", password="pass")
        self.client.post(
            self.url,
            {
                "received_messages[]": [self.received_message.id],
                "sent_messages[]": [self.sent_message.id],
            },
            secure=True,
        )
        # Both messages updated flags
        self.received_message.refresh_from_db()
        self.sent_message.refresh_from_db()
        self.assertTrue(self.received_message.is_deleted_by_receiver)
        self.assertTrue(self.sent_message.is_deleted_by_sender)

    def test_message_deleted_from_db_when_conditions_met(self):
        # Message already marked deleted by other party
        self.sent_message.is_deleted_by_receiver = True
        self.sent_message.save()
        self.client.login(username="user", password="pass")
        self.client.post(
            self.url, {"sent_messages[]": [self.sent_message.id]}, secure=True
        )
        # Should be deleted from DB
        self.assertFalse(Message.objects.filter(id=self.sent_message.id).exists())

    def test_redirect_for_anonymous_user(self):
        response = self.client.post(
            self.url,
            {"received_messages[]": [self.received_message.id]},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)
