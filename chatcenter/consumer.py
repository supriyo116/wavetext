import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()  # Get the User model

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']
        self.sender_username = self.scope['user'].username
        self.group_name = f'private_{self.sender_username}_{self.receiver_username}'

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver_username = text_data_json['receiver']

        # Get the sender and receiver User instances
        sender_user = await self.get_user(self.sender_username)
        receiver_user = await self.get_user(receiver_username)

        # Save the message to the database
        await database_sync_to_async(Message.objects.create)(
            sender=sender_user,
            receiver=receiver_user,
            message=message
        )

        # Send message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.sender_username,
                'timestamp': str(timezone.now())
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_user(self, username):
        """Helper function to get a User instance by username"""
        return User.objects.get(username=username)


#Group

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import GroupMessage, Group

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_group_name = f"group_{self.group_name}"

        # Join the group
        await self.channel_layer.group_add(
            self.group_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        group_name = text_data_json['group']
        sender = self.scope['user']

        # Fetch the group object
        try:
            group = await sync_to_async(Group.objects.get)(name=group_name)
        except Group.DoesNotExist:
            return  # Handle error (e.g., send an error message to the WebSocket)

        # Save message to the database
        await sync_to_async(GroupMessage.objects.create)(
            group=group,
            sender=sender,
            message=message,
            timestamp=timezone.now()
        )

        # Send message to group
        await self.channel_layer.group_send(
            self.group_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'timestamp': str(timezone.now())
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))
