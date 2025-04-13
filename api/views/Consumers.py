import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from models.models import Conversation, Message
from spotifyCloneBackend.presence import online_users, active_rooms

User = get_user_model()

class Consumers(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy user_id từ user đã xác thực
        self.user_id = str(self.scope["user"].id)  # Chuyển thành string để nhất quán
        # Lấy otherUserId từ query string
        query_string = self.scope["query_string"].decode()
        query_params = dict(qp.split("=") for qp in query_string.split("&") if qp)
        self.other_user_id = query_params.get("otherUserId")

        # # Kiểm tra nếu otherUserId không tồn tại hoặc trùng với user_id
        # if not self.other_user_id or self.other_user_id == self.user_id:
        #     await self.close()
        #     return

        # # Kiểm tra xem other_user_id có phải là artist (role_id=2) hay không
        # if User.objects.get(id=self.other_user_id).role_id == 2:
        #     await self.close()
        #     return

        # Kiểm tra xem otherUserId có online và trong room với user_id không
        existing_room = None
        if self.other_user_id in online_users:
            # Tìm room hiện có giữa user_id và otherUserId
            possible_room_name = "_".join(sorted([self.user_id, self.other_user_id]))  # ví dụ: "1_2"
            if possible_room_name in active_rooms:
                existing_room = possible_room_name

        # Nếu không có room chung hiện có, tạo mới
        if existing_room:
            self.room_name = existing_room
        else:
            self.room_name = "_".join(sorted([self.user_id, self.other_user_id]))  # ví dụ: "1_2"

        self.room_group_name = f'private_chat_{self.room_name}'

        # Thêm user vào danh sách online
        online_users[self.user_id] = self.channel_name

        # Lưu room vào active_rooms (nếu chưa có)
        active_rooms.add(self.room_name)

        # Join room
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