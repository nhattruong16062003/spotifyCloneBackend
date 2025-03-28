from django.db import models
from .playlist import Playlist
from .song import Song

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)  # Thứ tự bài hát trong playlist

    class Meta:
        unique_together = ('playlist', 'song')
        ordering = ['order']  # Sắp xếp mặc định theo thứ tự

    def __str__(self):
        return f"{self.playlist.name} - {self.song.title} (Order: {self.order})"
