# payments/urls.py
from django.urls import path
from .views import CreateRazorpayOrder, VerifyPayment

urlpatterns = [
    path('create/', CreateRazorpayOrder.as_view(), name='create-payment'),
    path('verify/', VerifyPayment.as_view(), name='verify-payment'),
]
