from rest_framework import serializers
from models.models import Conversation
from api.serializers.UserSerializer import UserSerializer
from api.serializers.MessageSerializer import MessageSerializer

class ConversationSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    has_unread = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'user1', 'user2', 'created_at', 'messages', 'last_message', 'has_unread']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-sent_at').first()
        if last:
            return MessageSerializer(last).data
        return None

    def get_has_unread(self, obj):
        return getattr(obj, 'has_unread', False)