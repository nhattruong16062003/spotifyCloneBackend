from django.db import models
from .user import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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

    def __str__(self):
        return f"Transaction {self.id} - {self.user.username} - {self.amount}"
