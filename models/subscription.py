from django.db import models
from .user import User

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=[('free', 'Free'), ('premium', 'Premium')])
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('expired', 'Expired')], default='active')

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
