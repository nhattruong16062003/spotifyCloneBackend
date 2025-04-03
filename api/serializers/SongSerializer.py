from rest_framework import serializers
from models.models import Song,ArtistCollab

class SongSerializer(serializers.ModelSerializer):
    # Thêm trường tùy chỉnh để lấy name từ user
    user = serializers.CharField(source='user.name', read_only=True)

    # Lấy danh sách nghệ sĩ hợp tác (collaborators)
    collab_artists = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'id',
            'title',
            'user',  # Chủ sở hữu bài hát
            'collab_artists',  # Danh sách nghệ sĩ hợp tác
            'description',
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
    def get_collab_artists(self, obj):
        """
        Lấy danh sách tên các nghệ sĩ hợp tác từ bảng ArtistCollab
        """
        artist_collabs = ArtistCollab.objects.filter(song=obj).select_related('user')
        return [collab.user.name for collab in artist_collabs if collab.user.name]