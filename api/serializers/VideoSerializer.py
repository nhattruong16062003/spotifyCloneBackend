from rest_framework import serializers
from models.models import Video, User
from api.serializers.UserSerializer import UserSerializer  # Assuming UserSerializer exists

class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)  # Nested serializer for user details
    play_count_recent = serializers.IntegerField(read_only=True, required=False)  # For trending play count

    class Meta:
        model = Video
        fields = [
            'id',  # Assuming Video has an implicit ID field
            'title',
            'description',
            'video_id',
            'image_path',
            'uploaded_by',
            'status',
            'uploaded_at',
            'updated_at',
            'play_count_recent',  # Include annotated play count
        ]
        read_only_fields = ['id', 'uploaded_at', 'updated_at', 'status']

    def to_representation(self, instance):
        # Customize output if needed, e.g., exclude play_count_recent if not present
        representation = super().to_representation(instance)
        if not hasattr(instance, 'play_count_recent'):
            representation.pop('play_count_recent', None)
        return representation