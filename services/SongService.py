from models.models import Song, SongPlayHistory
from django.db.models import Count
import random


class SongService:
    @staticmethod
    def add_song(data):
        song = Song.objects.create(**data)
        return song

    @staticmethod
    def get_song(song_id):
        try:
            return Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return None

    @staticmethod
    def update_song(song_id, data):
        try:
            song = Song.objects.get(id=song_id)
            for key, value in data.items():
                setattr(song, key, value)
            song.save()
            return song
        except Song.DoesNotExist:
            return None

    @staticmethod
    def delete_song(song_id):
        try:
            song = Song.objects.get(id=song_id)
            song.delete()
            return True
        except Song.DoesNotExist:
            return False
        
    @staticmethod
    def get_previous_song(current_song_id, user_id):
        """ Lấy bài hát được phát trước đó của user, nếu không có thì chọn ngẫu nhiên """
        try:
            # Lấy bài hát gần nhất đã nghe (không trùng với bài hiện tại)
            previous_song = (
                SongPlayHistory.objects
                .filter(user_id=user_id)
                .exclude(song_id=current_song_id)  # Loại bỏ bài hát hiện tại
                .order_by("-played_at")  # Lấy bài hát mới nhất trước đó
                .first()
            )
            if previous_song:
                return previous_song.song_id  # Trả về bài hát trước đó
        except SongPlayHistory.DoesNotExist:
            pass  # Nếu không có lịch sử, lấy bài ngẫu nhiên

        # Lấy tất cả bài hát khác ngoài bài hiện tại
        songs = Song.objects.exclude(id=current_song_id)    
        
        if songs.count() > 0:
            # Chọn bài hát ngẫu nhiên
            random_song = songs.order_by("?").first()
     
            return random_song.id

        return None  # Trả về None nếu không có bài hát nào trong hệ thống
    
    @staticmethod
    def get_next_song(current_song_id):        
        # Lấy tất cả bài hát khác ngoài bài hiện tại
        songs = Song.objects.exclude(id=current_song_id)    
        
        if songs.count() > 0:
            # Chọn bài hát ngẫu nhiên
            random_song = songs.order_by("?").first()
     
            return random_song.id
        else:
            return None

        
    @staticmethod
    def get_songs_by_artist(user_id):
        """Lấy toàn bộ bài hát của nghệ sĩ và tổng lượt nghe"""
        return Song.objects.filter(user_id=user_id) \
            .annotate(total_streams=Count('play_history')) \
            .values('id', 'title', 'image_path', 'duration', 'uploaded_at', 'total_streams') \
            .order_by('-uploaded_at')  # Sắp xếp bài hát mới nhất trước
