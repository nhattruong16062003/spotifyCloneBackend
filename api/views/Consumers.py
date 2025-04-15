import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from models.models import Conversation, Message
from spotifyCloneBackend.presence import online_users, active_rooms
from django.db.models import  Q
from django.db import transaction

User = get_user_model()

class Consumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = str(self.scope["user"].id)
        query_string = self.scope["query_string"].decode()
        query_params = dict(qp.split("=") for qp in query_string.split("&") if qp)
        self.other_user_id = str(query_params.get("otherUserId"))

        if not self.other_user_id or self.other_user_id == self.user_id:
            await self.close()
            return

        try:
            user1 = await database_sync_to_async(User.objects.get)(id=self.user_id)
            user2 = await database_sync_to_async(User.objects.get)(id=self.other_user_id)

            if user1 == user2:
                await self.close()
                return

            # Chuẩn hóa: user1 luôn có ID nhỏ hơn
            if int(self.user_id) < int(self.other_user_id):
                ordered_user1, ordered_user2 = user1, user2
            else:
                ordered_user1, ordered_user2 = user2, user1

            # Hàm đồng bộ để tìm hoặc tạo conversation
            def find_or_create_conversation():
                with transaction.atomic():
                    conversation = Conversation.objects.filter(
                        user1=ordered_user1, user2=ordered_user2
                    ).first()
                    if not conversation:
                        conversation = Conversation.objects.create(
                            user1=ordered_user1, user2=ordered_user2
                        )
                    return conversation

            # Gọi hàm đồng bộ thông qua database_sync_to_async
            conversation = await database_sync_to_async(find_or_create_conversation)()

        except User.DoesNotExist:
            await self.close()
            return

        self.room_name = "_".join(sorted([self.user_id, self.other_user_id]))
        self.room_group_name = f'private_chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "status",
            "message": f"User {self.user_id} joined room {self.room_name}"
        }))

    async def disconnect(self, close_code):
        # Xóa user khỏi danh sách online
        if self.user_id in online_users:
            del online_users[self.user_id]

        # Rời group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_id = data['receiver']
        sender_id = self.scope["user"].id

        # # Kiểm tra nếu sender và receiver trùng nhau
        # if sender_id == receiver_id:
        #     await self.send(text_data=json.dumps({
        #         "type": "error",
        #         "message": "Cannot send message to yourself"
        #     }))
        #     return

        # # Kiểm tra nếu receiver là artist (role_id=2)
        # if User.objects.get(id=receiver_id).role_id == 2:
        #     await self.send(text_data=json.dumps({
        #         "type": "error",
        #         "message": "Cannot send message to an artist"
        #     }))
        #     return

        await self.save_message(sender_id, receiver_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_id,
                'receiver': receiver_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender': event['sender'],
            'receiver': event['receiver'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)

            # # Kiểm tra lại lần nữa để đảm bảo
            # if sender_id == receiver_id:
            #     return
            # if receiver.role_id == 2:  # Artist có role_id=2
            #     return

            # Tạo hoặc lấy conversation
            conversation, _ = Conversation.objects.get_or_create(
                user1=sender if sender.id < receiver.id else receiver,
                user2=receiver if sender.id < receiver.id else sender,
            )

            # Tạo hoặc lấy conversation
            conversation, _ = Conversation.objects.get_or_create(
                user1=sender if sender.id < receiver.id else receiver,
                user2=receiver if sender.id < receiver.id else sender,
            )
            # Lưu tin nhắn
            Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=content,
            )
        except User.DoesNotExist:
            print(f"Error: User {sender_id} or {receiver_id} not found")