from django.db import models
from django.utils import timezone
from datetime import timedelta
from models.models import Song ,Playlist # Import các model
# from models.models import Song, Playlist, Album  # Import các model
from api.serializers.SongSerializer import SongSerializer  # Import serializers
from api.serializers.PlaylistSerializer import PlaylistSerializer  # Import serializers
from django.db.models import Count, Q


class TrendingService:
    @staticmethod
    def get_trending_songs(limit):  # Thay limit thành 10
        try:
            # Tính thời điểm 30 ngày trước
            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Lấy top 10 bài hát dựa trên số lượt nghe trong 30 ngày qua
            trending_songs = (
                Song.objects
                .annotate(play_count_recent=models.Count(
                    'play_history',  # Đếm lượt nghe từ SongPlayHistory
                    filter=models.Q(play_history__played_at__gte=thirty_days_ago)  # Chỉ tính trong 30 ngày
                ))
                .order_by('-play_count_recent')  # Sắp xếp theo số lượt nghe giảm dần
                [:limit]  # Giới hạn top 10
            )

            # Serialize dữ liệu
            return SongSerializer(trending_songs, many=True).data

        except Exception as e:
            print(f"Error fetching trending songs: {e}")
            return []
        
    @staticmethod
    def get_trending_playlists(limit):
        # Lấy ngày hiện tại và trừ đi 30 ngày
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        try:
            # Lấy danh sách các playlist và tổng số lượt nghe của các bài hát trong playlist trong 30 ngày gần nhất
            # chỉ tính lượt nghe từ playlist có user có role_id = 3 (user)
            trending_playlists = Playlist.objects.annotate(
                total_plays=Count(
                    'playlistsong__song__play_history',
                    filter=models.Q(playlistsong__song__play_history__played_at__gte=thirty_days_ago)
                )
            ).filter(user__role_id=3) 
            
            trending_playlists=trending_playlists.order_by('-total_plays')[:limit]
            
            # Serialize dữ liệu và trả về
            return PlaylistSerializer(trending_playlists, many=True).data
        except Exception as e:
            print(f"Error fetching trending playlists: {e}")
            return []


    def get_trending_albums(limit):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        try:
            # Lấy danh sách album có tổng số lượt nghe cao nhất trong 30 ngày gần nhất,
            # chỉ tính lượt nghe từ playlist có user có role_id = 2 (artist)
            trending_albums = Playlist.objects.annotate(
                total_plays=Count(
                    'playlistsong__song__play_history',
                    filter=models.Q(playlistsong__song__play_history__played_at__gte=thirty_days_ago)
                )
            ).filter(user__role_id=2) 

            # Giới hạn số lượng kết quả trả về
            trending_albums = trending_albums.order_by('-total_plays')[:limit]

            # Serialize dữ liệu và trả về
            return PlaylistSerializer(trending_albums, many=True).data
        except Exception as e:
            print(f"Error fetching trending albums: {e}")
            return []