# your_app_name/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from models.models import Conversation,Message
from api.serializers.ConversationSerializer import ConversationSerializer
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery, Max, Q
from rest_framework.pagination import PageNumberPagination


class ConversationPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationView(APIView):
    pagination_class = ConversationPagination
    def get(self, request):
        user = request.user

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


        last_msg_ids = [c.last_message_id for c in conversations if c.last_message_id]

        unread_ids = set(
            Message.objects.filter(
                id__in=last_msg_ids,
                is_read=False
            ).exclude(sender=user).values_list('id', flat=True)
        )

        convo_list = []
        for convo in conversations:
            convo.has_unread = convo.last_message_id in unread_ids
            convo_list.append(convo)

        convo_list.sort(
            key=lambda c: (not c.has_unread, -c.last_message_time.timestamp() if c.last_message_time else 0)
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(convo_list, request, view=self)
        serializer = ConversationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

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