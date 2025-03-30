from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import Song, Playlist, PlaylistSong
from api.serializers.PlaylistSerializer import PlaylistSerializer
from api.serializers.SongSerializer import SongSerializer  # Import SongSerializer

class PlaylistView(APIView):
    def get(self, request, playlist_id):
        try:
            # Lấy playlist theo ID
            playlist = Playlist.objects.get(id=playlist_id)
            
            # Serialize thông tin playlist
            playlist_serializer = PlaylistSerializer(playlist)
            
            # Lấy danh sách bài hát từ bảng PlaylistSong dựa vào playlist_id
            playlist_songs = PlaylistSong.objects.filter(playlist_id=playlist_id).select_related('song')
            
            # Serialize dữ liệu bài hát và thêm trường order
            songs_data = []
            for ps in playlist_songs:
                song_data = SongSerializer(ps.song).data  # Serialize bài hát
                song_data['order'] = ps.order  # Thêm trường order từ PlaylistSong
                songs_data.append(song_data)
            
            # Trả về cả thông tin playlist và danh sách bài hát
            return Response({
                "playlist": playlist_serializer.data,
                "songs": songs_data
            }, status=status.HTTP_200_OK)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)