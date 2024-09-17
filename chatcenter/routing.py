from django.urls import re_path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.staticfiles import StaticFilesWrapper  # For serving static files
from .consumer import PrivateChatConsumer, GroupChatConsumer

# WebSocket URL patterns for private and group chat
websocket_urlpatterns = [
    re_path(r'ws/chat/private/(?P<receiver_username>[^/]+)/$', PrivateChatConsumer.as_asgi()),
    re_path(r'ws/chat/group/(?P<group_name>\w+)/$', GroupChatConsumer.as_asgi()),
]

# Define the ASGI application for handling both HTTP and WebSocket requests
application = ProtocolTypeRouter({
    # HTTP protocol, with static files wrapped using StaticFilesWrapper
    "http": StaticFilesWrapper(
        get_asgi_application()
    ),
    # WebSocket protocol with URL routing
    "websocket": URLRouter(websocket_urlpatterns),
})
