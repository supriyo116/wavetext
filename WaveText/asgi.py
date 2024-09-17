import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chatcenter import routing
from channels.security.websocket import AllowedHostsOriginValidator
from chatcenter import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WaveText.settings')
import django
django.setup()
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))),
    })