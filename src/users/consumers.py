import json

from django.core.serializers import serialize
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from http.cookies import SimpleCookie
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from .models import Notification
from asgiref.sync import async_to_sync


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        user = await self.get_user_from_session()
        if user and user.is_authenticated:
            self.user_id = user.id
            self.group_name = f"user_{self.user_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            past_notifications = await self.get_all_notifications(user)

            for notification in past_notifications:
                await self.send_notification(
                    {
                        "id": notification.id,
                        "message": notification.message,
                        "is_read": notification.is_read,
                        "is_active": notification.is_active,
                        "timestamp": notification.timestamp.isoformat()[:-6],
                    }
                )

    async def disconnect(self, close_code):
        if hasattr(self, "user_id"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        notification_data = {
            "id": event.get("id"),
            "message": event.get("message"),
            "is_read": event.get("is_read"),
            "is_active": event.get("is_active"),
            "timestamp": event.get("timestamp"),
        }

        await self.send(text_data=json.dumps(notification_data))

    @database_sync_to_async
    def get_user_from_session(self):
        cookie_header = dict(self.scope.get("headers")).get(b"cookie", b"").decode()
        cookies = SimpleCookie()
        cookies.load(cookie_header)

        sessionid = cookies.get("sessionid")
        if sessionid:
            session_key = sessionid.value
            try:
                session = Session.objects.get(session_key=session_key)
                return User.objects.get(pk=session.get_decoded().get("_auth_user_id"))
            except (Session.DoesNotExist, User.DoesNotExist):
                return AnonymousUser()
        else:
            return AnonymousUser()

    @database_sync_to_async
    def get_all_notifications(self, user):
        return list(Notification.objects.filter(user=user, is_active=True))
