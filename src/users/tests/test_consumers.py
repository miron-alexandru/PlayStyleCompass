import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import TransactionTestCase

from asgiref.sync import async_to_sync
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path

from users.consumers import PresenceConsumer


User = get_user_model()


application = AuthMiddlewareStack(
    URLRouter(
        [
            path("ws/presence/", PresenceConsumer.as_asgi()),
        ]
    )
)


class PresenceConsumerTests(TransactionTestCase):
    async def _connect(self, user=None):
        # Create a test WebSocket connection
        communicator = WebsocketCommunicator(application, "/ws/presence/")
        communicator.scope["user"] = user or AnonymousUser()

        connected, _ = await communicator.connect()
        return communicator, connected

    def test_user_connect_marks_online(self):
        user = User.objects.create_user(
            username="atestuser",
            password="testpass",
        )

        communicator, connected = async_to_sync(self._connect)(user)

        self.assertTrue(connected)
        self.assertEqual(cache.get(f"online:{user.id}"), 1)

        async_to_sync(communicator.disconnect)()

    def test_guest_connection_is_rejected(self):
        communicator, connected = async_to_sync(self._connect)()
        self.assertFalse(connected)

    def test_disconnect_updates_last_seen(self):
        user = User.objects.create_user(
            username="ctestuser",
            password="testpass",
        )
        profile = user.userprofile

        communicator, _ = async_to_sync(self._connect)(user)
        async_to_sync(communicator.disconnect)()

        profile.refresh_from_db()
        self.assertIsNotNone(profile.last_online)

    def test_heartbeat_keeps_user_online(self):
        user = User.objects.create_user(
            username="dtestuser",
            password="testpass",
        )

        communicator, _ = async_to_sync(self._connect)(user)

        cache.set(f"online:{user.id}", 1, timeout=1)

        async_to_sync(communicator.send_to)(
            text_data=json.dumps({"type": "heartbeat"})
        )

        self.assertEqual(cache.get(f"online:{user.id}"), 1)

        async_to_sync(communicator.disconnect)()
