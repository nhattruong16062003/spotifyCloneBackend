from rest_framework import serializers
from models.models import Conversation
from api.serializers.UserSerializer import UserSerializer
from api.serializers.MessageSerializer import MessageSerializer

class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_user', 'last_message']

    def get_other_user(self, obj):
        user = self.context['request'].user
        other_user = obj.user2 if obj.user1 == user else obj.user1
        return UserSerializer(other_user).data

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None