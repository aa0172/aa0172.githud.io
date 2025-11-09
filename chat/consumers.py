import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Присоединяемся к группе комнаты
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Добавляем пользователя в активные
        if self.scope["user"].is_authenticated:
            room = ChatRoom.objects.get(name=self.room_name)
            if self.scope["user"] not in room.active_users.all():
                room.active_users.add(self.scope["user"])

            # Отправляем уведомление о подключении
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.scope["user"].username,
                    'user_count': room.active_users.count(),
                }
            )

        self.accept()

    def disconnect(self, close_code):
        # Убираем пользователя из активных
        if self.scope["user"].is_authenticated:
            try:
                room = ChatRoom.objects.get(name=self.room_name)
                if self.scope["user"] in room.active_users.all():
                    room.active_users.remove(self.scope["user"])

                # Отправляем уведомление об отключении
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'username': self.scope["user"].username,
                        'user_count': room.active_users.count(),
                    }
                )
            except ChatRoom.DoesNotExist:
                pass

        # Покидаем группу комнаты
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        if not self.scope["user"].is_authenticated:
            return

        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = text_data_json['message']
            username = text_data_json['username']
            user_id = text_data_json['user_id']

            if message.strip():  # Проверяем, что сообщение не пустое
                user = User.objects.get(id=user_id)
                room = ChatRoom.objects.get(name=self.room_name)

                # Сохраняем сообщение в базе данных
                message_obj = Message.objects.create(
                    room=room,
                    user=user,
                    content=message.strip()
                )

                # Отправляем сообщение в группу
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                        'user_id': user_id,
                        'timestamp': message_obj.timestamp.strftime('%H:%M'),
                        'message_id': message_obj.id,
                    }
                )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    def user_joined(self, event):
        self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_count': event['user_count'],
            'message': f'{event["username"]} присоединился к чату',
        }))

    def user_left(self, event):
        self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_count': event['user_count'],
            'message': f'{event["username"]} покинул чат',
        }))