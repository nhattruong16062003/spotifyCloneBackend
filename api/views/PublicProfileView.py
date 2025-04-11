from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from models.user import User
from api.serializers.UserSerializer import UserSerializer
from api.serializers.PlaylistSerializer import PlaylistSerializer
from models.models import Song, Playlist, PlaylistSong
from django.db.models import Count, Q
from api.serializers.SongSerializer import SongSerializer
from django.utils import timezone
from datetime import timedelta
from django.db import models


class PublicProfileView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, profile_id):
        if(request.path.startswith('/api/public-profile/albums/')):
            return self.get_albums_or_playlists_by_id(request, profile_id)
        elif(request.path.startswith('/api/public-profile/playlists/')):
            return self.get_albums_or_playlists_by_id(request, profile_id)
        if(request.path.startswith('/api/public-profile/popular-songs/')):
            return self.get_popular_songs_by_id(request, profile_id)

    def get_albums_or_playlists_by_id(self, request, profile_id):
        """
        Lấy danh sách album của artist theo id cua artist
        """
        try:
             # Lọc playlist theo user_id và lấy các trường cần thiết
            playlists = Playlist.objects.filter(user_id=profile_id) \
                .annotate(song_count=Count('playlistsong'))  # Thêm số lượng bài hát vào mỗi playlist
            # Lấy danh sách các playlist và số lượng bài hát
            playlist_data = playlists.values('id','image_path', 'created_at', 'name', 'song_count')

            return Response(list(playlist_data), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_popular_songs_by_id(self, request, profile_id):
        """
        Lấy danh sách 10 bài hát phổ biến nhất của artist dựa trên lượt nghe trong 30 ngày qua.
        
        Args:
            self: Instance của class (nếu dùng trong class-based view)
            request: HTTP request object
            profile_id: ID của artist/user để lọc bài hát
        
        Returns:
            Response: Đối tượng Response chứa dữ liệu serialized của các bài hát hoặc lỗi
        """
        try:
           
            # Tính thời điểm 30 ngày trước
            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Lấy top 10 bài hát phổ biến dựa trên lượt nghe trong 30 ngày qua
            trending_songs = (
                Song.objects
                .filter(user_id=profile_id)  # Lọc bài hát theo artist
                .annotate(play_count_recent=models.Count(
                    'play_history',  # Đếm lượt nghe từ SongPlayHistory
                    filter=models.Q(play_history__played_at__gte=thirty_days_ago)  # Chỉ tính trong 30 ngày
                ))
                .order_by('-play_count_recent')  # Sắp xếp theo số lượt nghe giảm dần
                [:10]  # Giới hạn top 10
            )
            # Serialize dữ liệu
            song_data = SongSerializer(trending_songs, many=True).data
            # Trả về Response với dữ liệu thành công
            return Response(
                {
                    "total": len(song_data),
                    "songs": song_data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Trả về Response với thông báo lỗi
            error_message = f"Error fetching popular songs for profile_id {profile_id}: {str(e)}"
            return Response(
                {"error": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )