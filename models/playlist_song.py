from django.db import models
from .playlist import Playlist
from .song import Song

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('playlist', 'song')

    def __str__(self):
        return f"{self.playlist.name} - {self.song.title}"
