from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notify/", consumers.NotificationConsumer.as_asgi()),
    path("ws/chat/<int:recipient_id>/", consumers.ChatConsumer.as_asgi()),
    path(
        "ws/online-status/<int:recipient_id>/", consumers.OnlineStatusConsumer.as_asgi()
    ),
    path("ws/online-status/", consumers.OnlineStatusConsumer.as_asgi()),
]
