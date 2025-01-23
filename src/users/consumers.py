"""This module contains WebSocket consumers for handling real-time communication
in the users application. Each consumer defines the behavior for specific WebSocket
events such as connection, disconnection, and message handling.
"""

import json
import asyncio
import pytz
from datetime import datetime

from http.cookies import SimpleCookie
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from .models import Notification, UserProfile, GlobalChatMessage, ChatMessage
from django.utils import timezone
from django.utils.translation import get_language
from django.conf import settings
from django.urls import reverse
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat


def get_user_from_session(scope):
    # Retrieve the cookie header from the scope
    cookie_header = dict(scope.get("headers")).get(b"cookie", b"").decode()

    # Parse the cookies
    cookies = SimpleCookie()
    cookies.load(cookie_header)

    # Get the session ID from the cookies
    sessionid = cookies.get("sessionid")

    if sessionid:
        # If session ID is found, get the session key
        session_key = sessionid.value
        try:
            # Try to retrieve the session using the session key
            session = Session.objects.get(session_key=session_key)

            # Get the user ID from the session and return the user object
            return User.objects.get(pk=session.get_decoded().get("_auth_user_id"))
        except (Session.DoesNotExist, User.DoesNotExist):
            # If the session or user does not exist, return an anonymous user
            return None
    else:
        # If no session ID is found, return an anonymous user
        return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for user notifications, managing connections,
    sending past notifications on connection, and broadcasting new notifications in real-time.
    """

    async def connect(self):
        await self.accept()
        user = await self.get_user_from_session()
        if user and user.is_authenticated:
            self.user_id = user.id
            self.group_name = f"user_{self.user_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            self.current_language = get_language()

            past_notifications = await self.get_all_notifications(user)

            for notification in past_notifications:
                notification_message = (
                    notification.message_ro if self.current_language == "ro" else notification.message
                )

                await self.send_notification(
                    {
                        "id": notification.id,
                        "message": notification.message,
                        "message_ro": notification.message_ro,
                        "is_read": notification.is_read,
                        "is_active": notification.is_active,
                        "timestamp": notification.timestamp.isoformat(),
                        "delivered": notification.delivered,
                    }
                )

    async def disconnect(self, close_code):
        if hasattr(self, "user_id"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):

        if self.current_language == "ro":
            notification_message = event.get("message_ro", event.get("message"))
        else:
            notification_message = event.get("message")

        notification_data = {
            "id": event.get("id"),
            "message": notification_message,
            "is_read": event.get("is_read"),
            "is_active": event.get("is_active"),
            "timestamp": event.get("timestamp"),
            "delivered": event.get("delivered"),
        }

        await self.send(text_data=json.dumps(notification_data))

    async def get_user_from_session(self):
        # Use the utility function to get the user from session
        return await database_sync_to_async(get_user_from_session)(self.scope)

    @database_sync_to_async
    def get_all_notifications(self, user):
        return list(
            Notification.objects.filter(user=user, is_active=True, delivered=True)
        )


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for chat functionality, managing user connections,
    message reception, and broadcasting typing indicators and message edits to all participants in a chat room.
    """

    async def connect(self):
        # Retrieve the user from the session
        self.user = await self.get_user_from_session()

        # Get the recipient ID from the URL route parameters
        self.recipient_id = self.scope["url_route"]["kwargs"]["recipient_id"]

        # Generate a unique room name using the user and recipient IDs
        self.room_name = f"chat_{self.user.id}_{self.recipient_id}"

        # Generate a unique group name to ensure both users join the same group
        self.room_group_name = f"chat_{min(self.user.id, self.recipient_id)}_{max(self.user.id, self.recipient_id)}"

        # Add the user to the channel layer group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the channel layer group on disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Parse the incoming WebSocket message as JSON
        text_data_json = json.loads(text_data)

        # Get the typing status and edit message data from the JSON data
        typing = text_data_json.get("typing", False)
        edit_message = text_data_json.get("edit_message", None)

        if edit_message:
            # Extract message details from the edit_message
            message_id = edit_message.get("message_id")
            new_content = edit_message.get("new_content")

            # Broadcast the edited message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message_edit",
                    "message_id": message_id,
                    "new_content": new_content,
                    "sender_id": self.user.id,
                },
            )
        else:
            # Send a message to the channel layer group with the typing status and sender ID
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "typing": typing,
                    "sender_id": self.user.id,
                },
            )

    async def chat_message(self, event):
        # Retrieve typing status and sender ID from the event and
        # send the typing status and sender ID back to the WebSocket client.
        typing = event["typing"]
        sender_id = event["sender_id"]

        await self.send(
            text_data=json.dumps(
                {
                    "typing": typing,
                    "sender_id": sender_id,
                }
            )
        )

    async def chat_message_edit(self, event):
        # Retrieve edited message details from the event
        message_id = event["message_id"]
        new_content = event["new_content"]
        sender_id = event["sender_id"]

        # Send the edited message details back to the WebSocket client
        await self.send(
            text_data=json.dumps(
                {
                    "message_id": message_id,
                    "new_content": new_content,
                    "sender_id": sender_id,
                }
            )
        )

    async def get_user_from_session(self):
        # Use the utility function to get the user from session
        return await database_sync_to_async(get_user_from_session)(self.scope)


class PrivateChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for private chat between two users.
    """

    async def connect(self):
        self.user = await self.get_user_from_session()
        self.recipient_id = self.scope["url_route"]["kwargs"]["recipient_id"]

        self.other_user = await self.get_user(self.recipient_id)
        if not self.other_user:
            await self.close()
            return

        self.room_group_name = self._generate_room_name(
            self.user.id, self.other_user.id
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_existing_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Process incoming WebSocket messages and broadcast to the group.
        """
        text_data_json = json.loads(text_data)

        message = text_data_json.get("message")
        file = text_data_json.get("file")
        file_size = text_data_json.get("file_size")
        is_pinned = text_data_json.get("is_pinned")
        edited = text_data_json.get("edited")
        message_id = text_data_json.get("message_id")

        profile_picture_url = await self.get_profile_picture_url(self.user)

        if message or file:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "private_chat_message",
                    "message": message,
                    "sender_id": self.user.id,
                    "recipient_id": self.other_user.id,
                    "file": file,
                    "file_size": file_size,
                    "created_at": datetime.now().isoformat(),
                    "profile_picture_url": profile_picture_url,
                    "is_pinned": is_pinned,
                    "edited": edited,
                    "id": message_id,
                },
            )

    async def private_chat_message(self, event):
        """
        Send the chat message event to the WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message": event.get("message"),
                    "sender_id": event["sender_id"],
                    "recipient_id": event["recipient_id"],
                    "file": event.get("file"),
                    "file_size": event.get("file_size"),
                    "created_at": event["created_at"],
                    "profile_picture_url": event["profile_picture_url"],
                    "edited": event.get("edited"),
                    "is_pinned": event.get("is_pinned"),
                    "id": event["id"],
                }
            )
        )

    def _generate_room_name(self, user_id_1, user_id_2):
        """
        Generate a consistent room group name for the chat room.
        """
        return f"private_chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"

    @database_sync_to_async
    def get_profile_picture_url(self, user):
        """
        Retrieve the profile picture URL for a given user.
        """
        return user.userprofile.profile_picture.url

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Fetch a User instance by ID.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_existing_messages(self, offset=0, limit=20):
        """
        Retrieve existing messages for the chat room, with sender/recipient filters.
        """
        messages = list(
            ChatMessage.objects.filter(
                (
                    Q(sender=self.user, recipient=self.other_user)
                    & ~Q(sender_hidden=True)
                )
                | (
                    Q(sender=self.other_user, recipient=self.user)
                    & ~Q(recipient_hidden=True)
                )
            )
            .annotate(
                profile_picture_url=Concat(
                    Value(settings.MEDIA_URL),
                    F("sender__userprofile__profile_picture"),
                    output_field=CharField(),
                ),
                is_pinned=Q(pinned_by__in=[self.user]),
            )
            .order_by("-created_at")
            .values(
                "id",
                "created_at",
                "content",
                "profile_picture_url",
                "sender_id",
                "edited",
                "file",
                "file_size",
                "is_pinned",
            )[offset : offset + limit]
        )
        messages.reverse()
        return messages

    async def send_existing_messages(self, offset=0, limit=20):
        """
        Send existing messages to the WebSocket client.
        """
        messages = await self.get_existing_messages(offset, limit)

        for message in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "id": message["id"],
                        "message": message["content"],
                        "sender_id": message["sender_id"],
                        "recipient_id": (
                            self.other_user.id
                            if message["sender_id"] == self.user.id
                            else self.user.id
                        ),
                        "file": message["file"],
                        "file_size": message["file_size"],
                        "created_at": message["created_at"].isoformat(),
                        "profile_picture_url": message["profile_picture_url"],
                        "is_pinned": message["is_pinned"],
                        "edited": message["edited"],
                    }
                )
            )

    async def get_user_from_session(self):
        """
        Retrieve the user associated with the current session.
        """
        return await database_sync_to_async(get_user_from_session)(self.scope)


class GlobalChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for the global chat room where all users can join and exchange messages.
    """

    async def connect(self):
        self.user = await self.get_user_from_session()
        self.room_group_name = "global_chat"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_existing_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def get_user_profile_name(self, user):
        """Retrieve the profile name of the user."""
        return user.userprofile.profile_name

    @database_sync_to_async
    def get_profile_picture_url(self, user):
        """Retrieve the profile picture URL for the user."""
        return user.userprofile.profile_picture.url

    def get_full_profile_picture_url(self, profile_picture_path):
        """Generates the full URL for the profile picture."""
        return f"{settings.MEDIA_URL}{profile_picture_path}"

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")

        if message:
            profile_picture_url = await self.get_profile_picture_url(self.user)
            profile_name = await self.get_user_profile_name(self.user)
            created_at = datetime.now().isoformat()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": self.user.id,
                    "sender_name": profile_name,
                    "profile_picture_url": profile_picture_url,
                    "created_at": created_at,
                },
            )

    async def chat_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]
        sender_name = event["sender_name"]
        profile_picture_url = event["profile_picture_url"]
        created_at = event["created_at"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender_id": sender_id,
                    "sender_name": sender_name,
                    "profile_picture_url": profile_picture_url,
                    "created_at": created_at,
                }
            )
        )

    async def get_user_from_session(self):
        """Retrieve the user from the session."""
        return await database_sync_to_async(get_user_from_session)(self.scope)

    @database_sync_to_async
    def get_existing_messages(self, offset=0, limit=20):
        messages = list(
            GlobalChatMessage.objects.all()
            .order_by("-created_at")
            .values(
                "id",
                "created_at",
                "content",
                "sender__id",
                "sender__userprofile__profile_name",
                "sender__userprofile__profile_picture",
            )[offset : offset + limit]
        )
        messages.reverse()

        return messages

    async def send_existing_messages(self, offset=0, limit=20):
        """Send existing messages to the WebSocket."""
        messages = await self.get_existing_messages(offset, limit)

        for message in messages:
            profile_picture_url = self.get_full_profile_picture_url(
                message["sender__userprofile__profile_picture"]
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "id": message["id"],
                        "message": message["content"],
                        "sender_id": message["sender__id"],
                        "sender_name": message["sender__userprofile__profile_name"],
                        "profile_picture_url": profile_picture_url,
                        "created_at": message["created_at"].isoformat(),
                    }
                )
            )


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve the recipient_id from the URL route
        self.recipient_id = self.scope["url_route"]["kwargs"].get("recipient_id")

        # Generate a unique group name for the recipient's status
        self.room_group_name = (
            f"user_status_{self.recipient_id}" if self.recipient_id else None
        )

        # Retrieve the user based on session information
        self.user = await self.get_user_from_session()

        # Ensure the user is authenticated
        if self.user and self.user.is_authenticated:
            await self.update_user_status(self.user.id, is_online=True)

            if self.room_group_name:
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )

            await self.accept()

            if self.recipient_id:
                user_profile = await self.get_user_profile(self.recipient_id)
                status = user_profile.is_online if user_profile else None
                last_online = await self.get_last_online(user_profile)

                await self.send(
                    text_data=json.dumps({"status": status, "last_online": last_online})
                )

            # Start periodic task to check user status
            self.periodic_task = asyncio.create_task(self.check_status_periodically())

    async def disconnect(self, close_code):
        """Update the user's status to offline"""
        if self.user and self.user.is_authenticated:
            await self.update_user_status(self.user.id, is_online=False)
        # Stop the periodic task
        if hasattr(self, "periodic_task"):
            self.periodic_task.cancel()

        # Leave the room group when the WebSocket disconnects
        if self.room_group_name:
            user_profile = await self.get_user_profile(self.user.id)
            last_online = await self.get_last_online(user_profile)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "status_update", "status": False, "last_online": last_online},
            )

            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def status_update(self, event):
        """Send status update to WebSocket client"""
        await self.send(
            text_data=json.dumps(
                {"status": event["status"], "last_online": event["last_online"]}
            )
        )

    async def check_status_periodically(self):
        """Periodically check and send user status every 15 seconds"""
        while True:
            if self.recipient_id:
                user_profile = await self.get_user_profile(self.recipient_id)
                status = user_profile.is_online if user_profile else None
                last_online = await self.get_last_online(user_profile)

                await self.send(
                    text_data=json.dumps({"status": status, "last_online": last_online})
                )
            await asyncio.sleep(15)

    async def get_last_online(self, user_profile):
        """Return formatted last_online time based on user_profile's timezone."""
        last_online = user_profile.last_online
        user_timezone = user_profile.timezone

        if last_online and user_timezone:
            user_tz = pytz.timezone(user_timezone)

            if last_online.tzinfo is None:
                last_online = timezone.make_aware(
                    last_online, timezone.get_default_timezone()
                )

            last_online = last_online.astimezone(user_tz)
            return last_online.strftime("%B %d, %Y, %I:%M %p")

        return None

    async def get_user_from_session(self):
        """Use the utility function to get the user from session"""
        return await database_sync_to_async(get_user_from_session)(self.scope)

    @database_sync_to_async
    def get_user_profile(self, user_id):
        """Fetch the user profile for the given user_id"""
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None

    @database_sync_to_async
    def update_user_status(self, user_id, is_online):
        """Update the user profile's status and last online time"""
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_profile.is_online = is_online
            user_profile.last_online = timezone.now()
            user_profile.save()
        except UserProfile.DoesNotExist:
            pass
