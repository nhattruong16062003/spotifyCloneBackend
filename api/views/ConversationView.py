# your_app_name/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from models.models import Conversation,Message
from api.serializers.ConversationSerializer import ConversationSerializer
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery, Max, Q

class ConversationView(APIView):
    def get(self, request):
        user = request.user  # current user

        # Lấy tất cả các conversation của user
        conversations = Conversation.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).annotate(
            last_message_time=Max('messages__sent_at'),
            last_message_id=Subquery(
                Message.objects.filter(conversation=OuterRef('pk'))
                .order_by('-sent_at')
                .values('id')[:1]
            )
        )

        # Lấy ID các message cuối cùng
        last_msg_ids = [c.last_message_id for c in conversations if c.last_message_id]

        # Tìm các message chưa đọc và được gửi bởi người khác
        unread_ids = set(
            Message.objects.filter(
                id__in=last_msg_ids,
                is_read=False
            ).exclude(sender=user).values_list('id', flat=True)
        )

        # Gán thêm biến phụ để hỗ trợ sorting
        convo_list = []
        for convo in conversations:
            convo.has_unread = convo.last_message_id in unread_ids
            convo_list.append(convo)

        # Sắp xếp: unread trước, rồi mới đến tin nhắn mới nhất
        convo_list.sort(key=lambda c: (not c.has_unread, -c.last_message_time.timestamp() if c.last_message_time else 0))

        # Trả về FE
        serializer = ConversationSerializer(convo_list, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    #Phương thức đánh dấu conversation đã được đọcđọc
    def post(self, request, conversation_id):
        user = request.user

        # Kiểm tra conversation hợp lệ
        conversation = get_object_or_404(
            Conversation.objects.filter(
                models.Q(user1=user) | models.Q(user2=user),
                id=conversation_id
            )
        )


        # Lấy last message (nếu có)
        last_message = conversation.messages.order_by('-sent_at').first()

        if last_message and last_message.sender != user and not last_message.is_read:
            last_message.is_read = True
            last_message.save()
            return Response({"detail": "Last message đã được đánh dấu là đã đọc."}, status=status.HTTP_200_OK)

        return Response({"detail": "Không cần đánh dấu, đã đọc hoặc không có tin nhắn."}, status=status.HTTP_200_OK)