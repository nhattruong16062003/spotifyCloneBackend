from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.TrendingService import TrendingService

class TrendingView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Lấy path từ request để xác định loại trending
            path = request.path
            
            if 'song' in path:
                data = TrendingService.get_trending_songs(limit=10)
                key = 'trending_songs'
            elif 'playlist' in path:
                data = TrendingService.get_trending_playlists(limit=10)
                key = 'trending_playlists'
            elif 'album' in path:
                data = TrendingService.get_trending_albums(limit=10)
                key = 'trending_albums'
            elif 'artists' in path:
                data = TrendingService.get_trending_artists(limit=10)
                key = 'trending_artists'
            else:
                return Response({"error": "Invalid trending type"}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra dữ liệu
            if not data:
                return Response({"error": f"No {key} data available"}, status=status.HTTP_404_NOT_FOUND)

            # Trả về dữ liệu với key tương ứng
            return Response({key: data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Failed to fetch trending data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)