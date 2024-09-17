from django.urls import re_path
from .consumer import *

websocket_urlpatterns = [

    re_path(r'ws/chat/private/(?P<receiver_username>[^/]+)/$', PrivateChatConsumer.as_asgi()),
    re_path(r'^ws/chat/group/(?P<group_name>\w+)/$', GroupChatConsumer.as_asgi()),
]