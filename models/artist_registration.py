from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ArtistRegistration(models.Model):
    artist_name = models.CharField(max_length=255)  # Nghệ danh của nghệ sĩ
    phone_number = models.CharField(max_length=15, unique=True, default="0000000000")  # Số điện thoại
    bio = models.TextField(blank=True, null=True)  # Giới thiệu về bản thân
    social_links = models.TextField(blank=True, null=True)  # Link mạng xã hội
    identity_proof = models.TextField(blank=True)   # Ảnh minh chứng
    artist_image = models.TextField(blank=True)  # Ảnh đại diện nghệ sĩ
    email = models.EmailField(unique=True, blank=False,default="default@example.com")  # Email nghệ sĩ (để dễ dàng xác thực)
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian gửi yêu cầu
    is_approved = models.BooleanField(default=False)  # Trạng thái duyệt của admin
    deleted_at = models.DateTimeField(blank=True, null=True)  # Hủy yêu cầu đăng kí trở thành artist

    def __str__(self):
        return f"{self.artist_name} - {self.email}"
