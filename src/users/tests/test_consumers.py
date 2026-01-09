import json
import asyncio

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.core.cache import cache

from asgiref.sync import async_to_sync
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path
from django.contrib.auth.models import AnonymousUser

from users.consumers import PresenceConsumer, NotificationConsumer
from users.models import Notification


User = get_user_model()

application = AuthMiddlewareStack(
    URLRouter(
        [
            path("ws/presence/", PresenceConsumer.as_asgi()),
            path("ws/notifications/", NotificationConsumer.as_asgi()),
        ]
    )
)



class PresenceConsumerTests(TransactionTestCase):
    async def _connect(self, user=None):
        communicator = WebsocketCommunicator(
            application,
            "/ws/presence/",
        )

        communicator.scope["user"] = user or AnonymousUser()

        connected, _ = await communicator.connect()
        return communicator, connected

    def _safe_disconnect(self, communicator):
        try:
            async_to_sync(communicator.disconnect)()
        except asyncio.CancelledError:
            pass

    def test_user_connect_marks_online(self):
        user = User.objects.create_user(
            username="atestuser",
            password="testpass"
        )

        communicator = None
        try:
            communicator, connected = async_to_sync(self._connect)(user)

            self.assertTrue(connected)
            self.assertEqual(cache.get(f"online:{user.id}"), 1)
        finally:
            if communicator:
                self._safe_disconnect(communicator)

    def test_guest_connection_is_rejected(self):
        communicator = None
        try:
            communicator, connected = async_to_sync(self._connect)()
            self.assertFalse(connected)
        finally:
            if communicator:
                self._safe_disconnect(communicator)

    def test_disconnect_updates_last_seen(self):
        user = User.objects.create_user(
            username="ctestuser",
            password="testpass"
        )
        profile = user.userprofile

        communicator = None
        try:
            communicator, _ = async_to_sync(self._connect)(user)
        finally:
            if communicator:
                self._safe_disconnect(communicator)

        profile.refresh_from_db()
        self.assertIsNotNone(profile.last_online)

    def test_heartbeat_keeps_user_online(self):
        user = User.objects.create_user(
            username="dtestuser",
            password="testpass",
        )

        communicator = None
        try:
            communicator, connected = async_to_sync(self._connect)(user)
            assert connected

            cache.set(f"online:{user.id}", 1, timeout=5)

            async_to_sync(communicator.send_to)(
                text_data=json.dumps({"type": "heartbeat"})
            )

            async_to_sync(asyncio.sleep)(0.1)

            self.assertEqual(cache.get(f"online:{user.id}"), 1)
        finally:
            if communicator:
                self._safe_disconnect(communicator)


class NotificationConsumerTests(TransactionTestCase):
    async def _connect(self, user=None):
        """
        Helper to connect a user or guest to the notifications WebSocket.
        Returns (communicator, connected).
        """
        communicator = WebsocketCommunicator(application, "/ws/notifications/")
        communicator.scope["user"] = user or AnonymousUser()
        connected, _ = await communicator.connect()
        return communicator, connected

    def _safe_disconnect(self, communicator):
        """
        Disconnect communicator safely without raising CancelledError.
        """
        try:
            async_to_sync(communicator.disconnect)()
        except asyncio.CancelledError:
            pass

    def test_user_receives_notifications(self):
        """
        Authenticated user should receive all past active and delivered notifications
        immediately upon connecting.
        """
        user = User.objects.create_user(username="ntestuser", password="testpass")

        Notification.objects.create(
            user=user,
            message="Hello",
            message_ro="Salut",
            is_read=False,
            is_active=True,
            delivered=True,
        )

        async def run():
            communicator = WebsocketCommunicator(application, "/ws/notifications/")
            communicator.scope["user"] = user

            connected, _ = await communicator.connect()
            assert connected

            data = await communicator.receive_json_from()
            await communicator.disconnect()
            return data

        data = async_to_sync(run)()
        self.assertEqual(data["message"], "Hello")
        self.assertFalse(data["is_read"])

    def test_inactive_notifications_not_sent(self):
        """
        Inactive notifications are not delivered to the user.
        """
        user = User.objects.create_user(
            username="ntestuser2",
            password="testpass",
        )

        Notification.objects.create(
            user=user,
            message="Hidden",
            message_ro="Ascuns",
            is_read=False,
            is_active=False,
            delivered=True,
        )

        async def run():
            communicator, connected = await self._connect(user)
            assert connected

            try:
                await communicator.receive_json_from(timeout=0.5)
                self.fail("Inactive notification was sent")
            except asyncio.TimeoutError:
                pass

            await communicator.disconnect()

        async_to_sync(run)()

    def test_guest_receives_nothing(self):
        """
        Guest connections are accepted but receive no notifications.
        """
        async def run():
            communicator, connected = await self._connect()
            assert connected

            try:
                await communicator.receive_json_from(timeout=0.5)
                self.fail("Guest received a message")
            except asyncio.TimeoutError:
                pass

            await communicator.disconnect()

        async_to_sync(run)()