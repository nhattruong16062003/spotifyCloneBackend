import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count
from models.models import Song, User, Playlist, Video
from api.serializers.UserSerializer import UserSerializer
from api.serializers.PlaylistSerializer import PlaylistSerializer
from api.serializers.SongSerializer import SongSerializer
from rest_framework import status
from services.TrendingService import TrendingService
from services.SearchService import SearchService
from api.serializers.VideoSerializer import VideoSerializer  


class SearchView(APIView):
    def get(self, request, keyword=None, *args, **kwargs):
        data_type = request.query_params.get('selectedType', None)
        keyword= request.query_params.get('searchKeyword', None)
        # Lấy user_id nếu đã đăng nhập
        user_id = None
        if request.user and request.user.is_authenticated:
            user_id = request.user.id

        try:
            limit = int(request.query_params.get('limit', 15))
        except (TypeError, ValueError):
            limit = 15  # fallback nếu không phải số

        try:
            offset = int(request.query_params.get('offset', 0))
        except (TypeError, ValueError):
            offset = 0  # fallback nếu không phải số

        # Lấy dữ liệu trending trong trường hợp không có keyword
        if not keyword or not keyword.strip():
            if data_type == "artist":
                trending_songs = TrendingService.get_trending_songs(20)
                # Lấy danh sách nghệ sĩ từ bài hát đã lọc
                artist_ids = [song['artist_id'] for song in trending_songs]
                artists = User.objects.filter(id__in=artist_ids, role_id=2)
                serializer = UserSerializer(artists, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif data_type == "playlist":
                trending_playlists = TrendingService.get_trending_playlists(20)
                serializer = PlaylistSerializer(trending_playlists, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif data_type == "album":
                trending_albums = TrendingService.get_trending_albums(20)
                serializer = PlaylistSerializer(trending_albums, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif data_type == "song":
                trending_songs = TrendingService.get_trending_songs(20)
                serializer = SongSerializer(trending_songs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif data_type == "video":
                trending_videos = TrendingService.get_trending_videos(20)
                serializer = VideoSerializer(trending_videos, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid type parameter'}, status=status.HTTP_400_BAD_REQUEST)

        # Gọi SearchService với user_id (có thể là None nếu không đăng nhập)
        queryset = SearchService.search(data_type, keyword, limit, offset, user_id=user_id)

        # Xử lý trường hợp không hợp lệ hoặc không tìm thấy dữ liệu
        if queryset is None:
            if data_type in ["playlists", "albums", "videos"]:
                return Response({'error': f'No {data_type} found'}, status=status.HTTP_404_NOT_FOUND)
            print(f"Invalid request received with type: {data_type} and keyword: {keyword}")
            return Response({'error': 'Invalid type parameter'}, status=status.HTTP_400_BAD_REQUEST)


        if data_type in ["users", "artists"]:
            serializer = UserSerializer(queryset, many=True)
        elif data_type == "songs":
            serializer = SongSerializer(queryset, many=True)
        elif data_type in ["playlists", "albums"]:
            serializer = PlaylistSerializer(queryset, many=True)
        elif data_type == "videos": 
            serializer = VideoSerializer(queryset, many=True)

        # Trả về kết quả phân trang
        return Response(serializer.data, status=status.HTTP_200_OK)