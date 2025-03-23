from django.shortcuts import get_object_or_404
from models.models import Song, User,SongPlayHistory
from django.utils.timezone import now
import pytz


class SongPlayHistoryService:
    @staticmethod
    def save_play_history(song_id, user_id):
        song = get_object_or_404(Song, id=song_id)
        user = get_object_or_404(User, id=user_id)

        # Chuyển đổi thời gian sang múi giờ Việt Nam (GMT+7)
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        played_at_vn = now().astimezone(vietnam_tz)
        print(played_at_vn)

        # Lưu lịch sử phát nhạc
        return SongPlayHistory.objects.create(song=song, user=user, played_at=played_at_vn)
