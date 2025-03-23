from django.db import models
from .user import User

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)  # New field for image path

    def __str__(self):
        return self.name
