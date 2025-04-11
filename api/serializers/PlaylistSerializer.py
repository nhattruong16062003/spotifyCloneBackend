from rest_framework import serializers
from models.playlist import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)  # Truy cập user.name

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'image_path', 'username','description']  # Thêm username vào fields

