from django.db import models

class PremiumPlan(models.Model):
    """Bảng lưu thông tin gói Premium"""
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()  # Số ngày sử dụng gói

    def __str__(self):
        return f"{self.name} - {self.price}₫ ({self.duration_days} ngày)"
