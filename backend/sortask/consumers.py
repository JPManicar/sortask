import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        user = await self.get_user()
        if not isinstance(user, AnonymousUser):
            await self.channel_layer.group_add(f"notifications_{user.id}", self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = await self.get_user()
        if not isinstance(user, AnonymousUser):
            await self.channel_layer.group_discard(f"notifications_{user.id}", self.channel_name)

    async def send_notification(self, event):
        message = event['message']
        timestamp = event['timestamp']
        await self.send(text_data=json.dumps({'message': message, 'timestamp': timestamp.isoformat()}))

    @database_sync_to_async
    def get_user(self):
        headers = dict(self.scope.get('headers', []))
        token = headers.get(b'authorization', None).decode(
            'utf-8').split(' ')[1]

        if token:
            try:
                authentication = JWTAuthentication()
                validated_token = authentication.get_validated_token(token)
                user = authentication.get_user(validated_token)
                return user
            except AuthenticationFailed:
                return AnonymousUser()
        else:
            return AnonymousUser()
