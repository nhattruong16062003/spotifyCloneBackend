from django.db import models
from django.utils import timezone
from .user import User
from .video import Video


class VideoPlayHistory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='play_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_play_history')
    played_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-played_at']  # Sắp xếp theo thời gian phát mới nhất
        indexes = [
            models.Index(fields=['user', 'played_at']),
            models.Index(fields=['video', 'played_at']),
        ]  # Tối ưu truy vấn

    def __str__(self):
        return f"{self.user.username} played {self.video.title} at {self.played_at}"