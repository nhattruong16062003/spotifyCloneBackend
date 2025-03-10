from django.db import models
from .artist import Artist

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.CharField(max_length=255, null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    duration = models.PositiveIntegerField()  # Duration in seconds
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
