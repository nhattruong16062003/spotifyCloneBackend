from django.db import models
from .user import User

class Video(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    video_id = models.CharField(max_length=255, null=True, blank=True)
    image_path = models.URLField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']  # Sắp xếp theo thời gian upload mới nhất

    def __str__(self):
        return self.title