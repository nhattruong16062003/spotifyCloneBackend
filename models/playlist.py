from django.db import models
from .user import User

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # Thêm trường mô tả playlist
    created_at = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)  # New field for image path
    play_count = models.PositiveIntegerField(default=0)  # Trường đếm số lần phát

    def __str__(self):
        return self.name
