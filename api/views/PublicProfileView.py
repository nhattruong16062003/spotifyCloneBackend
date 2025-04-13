from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from models.user import User
from models.artist_collab import ArtistCollab
from api.serializers.UserSerializer import UserSerializer
from api.serializers.PlaylistSerializer import PlaylistSerializer
from models.models import Song, Playlist, PlaylistSong
from django.db.models import Count, Q
from api.serializers.SongSerializer import SongSerializer
from django.utils import timezone
from datetime import timedelta
from django.db import models
from rest_framework.pagination import PageNumberPagination


class ConversationPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

class PublicProfileView(APIView):
    pagination_class = ConversationPagination  # Đặt pagination class cho view
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
        Lấy danh sách bài hát phổ biến nhất của artist (bao gồm collab) với phân trang.
        """
        try:
            # Kiểm tra xem user có tồn tại không
            if not User.objects.filter(id=profile_id).exists():
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Lấy ID bài hát của artist và bài hát collab
            own_song_ids = Song.objects.filter(user_id=profile_id).values_list('id', flat=True)
            collab_song_ids = ArtistCollab.objects.filter(user_id=profile_id).values_list('song', flat=True)

            # Hợp nhất danh sách ID bài hát
            all_song_ids = set(own_song_ids) | set(collab_song_ids)

            # Lấy bài hát và sắp xếp theo uploaded_at
            songs = Song.objects.filter(id__in=all_song_ids).order_by('-uploaded_at')

            # Áp dụng phân trang
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(songs, request, view=self)

            # Serialize dữ liệu
            serializer = SongSerializer(page, many=True, context={'request': request})

            # Trả về response với phân trang
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Error fetching popular songs for profile_id {profile_id}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )