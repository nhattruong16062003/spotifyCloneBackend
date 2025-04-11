from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from models.models import Conversation, Message
from api.serializers.MessageSerializer import MessageSerializer

User = get_user_model()

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, other_user_id):
        try:
            other_user = User.objects.get(id=other_user_id)
            # Find conversation where request.user is user1 and other_user is user2, or vice versa
            conversation = Conversation.objects.filter(
                user1=request.user, user2=other_user
            ).first() or Conversation.objects.filter(
                user1=other_user, user2=request.user
            ).first()

            if not conversation:
                # Create a new conversation if none exists
                conversation = Conversation.objects.create(
                    user1=request.user if request.user.id < other_user.id else other_user,
                    user2=other_user if request.user.id < other_user.id else request.user
                )

            # Fetch messages for the conversation
            messages = Message.objects.filter(conversation=conversation).order_by('sent_at')
            serializer = MessageSerializer(messages, many=True)
            return Response({
                'conversation_id': conversation.id,
                'messages': serializer.data
            })
        except User.DoesNotExist:
            return Response({"error": "Other user not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)