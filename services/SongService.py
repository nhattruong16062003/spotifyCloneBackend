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
                return previous_song.song  # Trả về bài hát trước đó
        except SongPlayHistory.DoesNotExist:
            pass  # Nếu không có lịch sử, lấy bài ngẫu nhiên

        # Lấy bài hát ngẫu nhiên nếu không tìm thấy bài hát trước đó
        song_count = Song.objects.count()
        if song_count > 0:
            random_song = Song.objects.order_by("?").first()  # Lấy bài ngẫu nhiên
            return random_song

        return None  # Trả về None nếu không có bài hát nào trong hệ thống