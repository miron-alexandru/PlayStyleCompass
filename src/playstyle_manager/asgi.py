import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from users.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playstyle_manager.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns)),
    }
)
