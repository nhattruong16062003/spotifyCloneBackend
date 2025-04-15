from django.db import models
from django.utils import timezone
from datetime import timedelta
from models.models import Song ,Playlist,User ,Video
# from models.models import Song, Playlist, Album  # Import các model
from api.serializers.SongSerializer import SongSerializer  # Import serializers
from api.serializers.PlaylistSerializer import PlaylistSerializer  # Import serializers
from django.db.models import Count, Q
from api.serializers.UserSerializer import UserSerializer  # Import serializer cho Artist



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
    
    @staticmethod
    def get_trending_artists(limit=10):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        try:
            # Lấy danh sách nghệ sĩ có tổng số lượt nghe bài hát cao nhất trong 30 ngày qua
            trending_artists = (
                Song.objects
                .filter(play_history__played_at__gte=thirty_days_ago)  # Lọc các bài hát có lượt nghe trong 30 ngày
                .values('user')  # Nhóm theo user (nghệ sĩ)
                .annotate(total_plays=Count('playbackhistory'))  # Đếm tổng số lượt nghe
                .order_by('-total_plays')  # Sắp xếp theo số lượt nghe giảm dần
                [:limit]  # Giới hạn số lượng kết quả
            )

            # Lấy thông tin chi tiết của các nghệ sĩ từ danh sách user IDs
            artist_ids = [artist['user'] for artist in trending_artists]
            trending_artists = (
                User.objects
                .filter(id__in=artist_ids, role__name='artist', is_active=True)  # Chỉ lấy nghệ sĩ (role=artist) và đang hoạt động
                .select_related('role')  # Tối ưu hóa truy vấn liên quan đến role
            )

            # Serialize dữ liệu
            return UserSerializer(trending_artists, many=True).data

        except Exception as e:
            print(f"Error fetching trending artists: {str(e)}")
            return []
        
    @staticmethod
    def get_trending_videos(limit=10):
        try:
            # Calculate the date 30 days ago
            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Get top videos based on play count in the last 30 days
            trending_videos = (
                Video.objects
                .annotate(play_count_recent=Count(
                    'play_history',
                    filter=Q(play_history__played_at__gte=thirty_days_ago)
                ))
                .order_by('-play_count_recent')  # Sort by play count descending
                [:limit]  # Limit to specified number
            )

            # Serialize data (assuming a VideoSerializer exists)
            from api.serializers.VideoSerializer import VideoSerializer
            return VideoSerializer(trending_videos, many=True).data

        except Exception as e:
            print(f"Error fetching trending videos: {str(e)}")
            return []