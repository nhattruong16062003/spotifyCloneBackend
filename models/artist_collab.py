from django.db import models
from .song import Song
from .user import User

class ArtistCollab(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Ca sĩ
    song = models.ForeignKey(Song, on_delete=models.CASCADE)  # Bài hát

    class Meta:
        unique_together = ('user', 'song')  # Đảm bảo không có ca sĩ nào bị lặp với cùng một bài hát

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"
