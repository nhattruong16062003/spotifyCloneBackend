from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from models.models import Playlist, PlaylistSong, Song
from api.serializers.PlaylistSerializer import PlaylistSerializer
from services.PlaylistService import PlaylistService

class PlaylistView(APIView):
    def get(self, request, song_id):
        """API lấy danh sách playlist của user nhưng chưa chứa song_id"""
        if request.path.endswith(f"/api/playlist/user/{song_id}/"):  # Kiểm tra URL
            user_id = request.user.id  # Nếu dùng authentication
            playlists = Playlist.objects.filter(user_id=user_id).exclude(playlistsong__song_id=song_id)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """API tạo playlist hoặc thêm bài hát vào nhiều playlist"""
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