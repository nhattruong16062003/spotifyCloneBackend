from rest_framework import serializers
from models.playlist import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Truy cập user.username

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'image_path', 'username']  # Thêm username vào fields

