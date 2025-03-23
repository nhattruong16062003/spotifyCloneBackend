from rest_framework import serializers
from models.models import Song

class SongSerializer(serializers.ModelSerializer):
    # Thêm trường tùy chỉnh để lấy username từ user
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id',
            'title',
            'user',  # Sử dụng trường tùy chỉnh đã định nghĩa ở trên
            'album',
            'genre',
            'duration',
            'mp3_path',
            'image_path',
            'uploaded_at',
            'play_count'
        ]
        extra_kwargs = {
            'uploaded_at': {'read_only': True},  # Không cho phép chỉnh sửa uploaded_at
            'play_count': {'read_only': True}    # Không cho phép chỉnh sửa play_count qua API
        }