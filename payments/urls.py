from django.urls import path
from .VNpayView import VNpayView
from .CashView import CashView

urlpatterns = [
    path('create-payment/', VNpayView.as_view(), name='create_payment'),
    path('payment-return/', VNpayView.as_view(), name='payment_return'),
    path('cash-payment/', CashView.as_view(), name='cash-payment'),

]