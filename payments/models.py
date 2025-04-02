# models.py của payment

from django.db import models
from models.models import User  # Hoặc import User model của bạn

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    txn_ref = models.CharField(max_length=255)  # Thêm trường txn_ref
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_info = models.CharField(max_length=255)  # Thêm trường order_info
    payment_method = models.CharField(
        max_length=20, 
        choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('google_pay', 'Google Pay')]
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], 
        default='pending'
    )
    response_code = models.CharField(max_length=50, null=True, blank=True)  # Thêm trường response_code

    def __str__(self):
        return f"Transaction {self.id} - {self.user.username} - {self.amount}"
