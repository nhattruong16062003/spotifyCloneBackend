from django.db import models
from django.utils import timezone
from datetime import timedelta
from .user import User
from .premium_plan import PremiumPlan
from payments.models import Transaction

class PremiumSubscription(models.Model):
    """Bảng lưu thông tin đăng ký Premium của người dùng"""
    user = models.ForeignKey(User, related_name="premium_subscriptions", on_delete=models.CASCADE)
    plan = models.ForeignKey(PremiumPlan, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction,max_length=100, unique=True, null=True, blank=True,on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)  # Cho phép tùy chỉnh
    end_date = models.DateTimeField()

    class Meta:
        # Đảm bảo mỗi user chỉ có một subscription với một transaction duy nhất
        unique_together = ('user', 'transaction')

    def save(self, *args, **kwargs):
        """Tự động tính toán end_date dựa trên start_date và duration của plan"""
        if not self.pk or self.start_date != self._meta.get_field('start_date').default():
            # Chỉ cập nhật end_date khi tạo mới hoặc start_date thay đổi
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def is_active(self):
        """Kiểm tra xem gói này còn hiệu lực hay không"""
        return self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} (Hết hạn: {self.end_date})"