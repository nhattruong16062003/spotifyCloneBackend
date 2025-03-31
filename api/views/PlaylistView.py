
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models.models import Song, Playlist, PlaylistSong
from api.serializers.PlaylistSerializer import PlaylistSerializer
from api.serializers.SongSerializer import SongSerializer  # Import SongSerializer
from services.PlaylistService import PlaylistService

class PlaylistView(APIView):
    def get(self, request, song_id=None, playlist_id=None):
        """API lấy danh sách playlist của user nhưng chưa chứa song_id"""
        if request.path.endswith(f"/api/playlist/user/{song_id}/"):  # Kiểm tra URL
            user_id = request.user.id  # Nếu dùng authentication
            playlists = Playlist.objects.filter(user_id=user_id).exclude(playlistsong__song_id=song_id)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.path.endswith(f"/api/playlists/{playlist_id}/songs/"):
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
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """API tạo playlist hoặc thêm bài hát vào nhiều playlist"""
        # Kiểm tra người dùng đã login chưa
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        data = request.data
        user_id = request.user.id  # Nếu dùng authentication

        if "name" in data:  # Nếu có 'name', thực hiện tạo playlist mới
            user_id = request.user.id  # Nếu dùng authentication

            result, status_code = PlaylistService.create_playlist(user_id, data["name"])
            return Response(result, status=status_code)

        if not request.path.endswith("/api/playlist/add-song/"):
            return Response({"error": "Invalid request path"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý thêm bài hát vào playlist (giữ nguyên code cũ)
        song_id = data.get("song_id")
        playlist_ids = data.get("playlists", [])  

        if not song_id or not playlist_ids:
            return Response({"error": "Thiếu song_id hoặc danh sách playlist_ids"}, status=status.HTTP_400_BAD_REQUEST)

        result, status_code = PlaylistService.add_song_to_playlists(user_id, song_id, playlist_ids)
        return Response(result, status=status_code)