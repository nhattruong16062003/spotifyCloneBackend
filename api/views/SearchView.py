import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count
from models.models import Song, User, Playlist
from api.serializers.UserSerializer import UserSerializer
from api.serializers.PlaylistSerializer import PlaylistSerializer
from api.serializers.SongSerializer import SongSerializer
from rest_framework import status
from services.TrendingService import TrendingService

class Pagination(LimitOffsetPagination):
    default_limit = 15
    max_limit = 50
    
class SearchView(APIView):
    def get(self, request, keyword=None, *args, **kwargs):
        data_type = request.query_params.get('type', None)
        
        # Lấy dữ liệu trending trong trường hợp không có keyword
        if not keyword or not keyword.strip():
            if data_type == "user":
                user_id = request.user.id
                return Response(User.objects.get(id = user_id), status=status.HTTP_200_OK)
            elif data_type == "artist":
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
            else:
                return Response({'error': 'Invalid type parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        pagination = Pagination()
        
        # Lọc từng kiểu dữ liệu khác nhau
        if data_type == "user":
            queryset = User.objects.filter(username__icontains=keyword, role_id=3)
            paginated = pagination.paginate_queryset(queryset, request)
            serializer = UserSerializer(paginated, many=True)
            return Response(pagination.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

        elif data_type == "artist":
            queryset = User.objects.filter(username__icontains=keyword, role_id=2)
            paginated = pagination.paginate_queryset(queryset, request)
            serializer = UserSerializer(paginated, many=True)
            return Response(pagination.get_paginated_response(serializer.data),  status=status.HTTP_200_OK)

        elif data_type == "song":
            queryset = Song.objects.filter(title__icontains=keyword)
            paginated = pagination.paginate_queryset(queryset, request)
            serializer = SongSerializer(paginated, many=True)
            return Response(pagination.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

        elif data_type == "playlist":
            queryset = Playlist.objects.filter(name__icontains=keyword, user__role_id=3)
            paginated = pagination.paginate_queryset(queryset, request)
            serializer = PlaylistSerializer(paginated, many=True)
            return Response(pagination.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

        elif data_type == "album":
            queryset = Playlist.objects.filter(name__icontains=keyword, user__role_id=2)
            paginated = pagination.paginate_queryset(queryset, request)
            serializer = PlaylistSerializer(paginated, many=True)
            return Response(pagination.get_paginated_response(serializer.data), status=status.HTTP_200_OK)
        
        else:
            return Response({'error': 'Invalid type parameter'}, status=status.HTTP_400_BAD_REQUEST)