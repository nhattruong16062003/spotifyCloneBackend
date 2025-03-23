from rest_framework import serializers
from models.playlist import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'image_path']  # Chỉ trả về ID, tên và ảnh playlist
