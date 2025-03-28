from django.db import models
from .user import User

class Song(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)  
    genre = models.CharField(max_length=100, null=True, blank=True)
    duration = models.PositiveIntegerField()  # Duration in seconds
    mp3_path = models.CharField(max_length=255)  # Renamed from file_path
    image_path = models.CharField(max_length=255, null=True, blank=True)  # New field for image path
    uploaded_at = models.DateTimeField(auto_now_add=True)
    play_count = models.PositiveIntegerField(default=0)  # Tổng số lượt nghe (có thể tính từ bảng SongPlayHistory)

    def __str__(self):
        return self.title
