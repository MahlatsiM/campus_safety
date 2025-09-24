import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import safety.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_safety_platform.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            safety.routing.websocket_urlpatterns
        )
    ),
})
