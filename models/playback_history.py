from django.db import models
from .user import User
from .song import Song

class PlaybackHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} played {self.song.title} at {self.played_at}"
