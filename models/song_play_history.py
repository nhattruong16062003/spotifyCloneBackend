from django.db import models
from .user import User
from .song import Song
from django.utils.timezone import now

class SongPlayHistory(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="play_history")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Nếu user không bắt buộc, có thể để null
    played_at = models.DateTimeField(default=now)  # Thời điểm nghe

    def __str__(self):
        return f"{self.song.title} - {self.played_at}"
