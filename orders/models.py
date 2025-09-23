from django.db import models
from users.models import User
from food.models import FoodItem


class DeliveryAddress(models.Model):
    """
    Stores delivery address details associated with a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="delivery_addresses")
    full_name = models.CharField(max_length=100, null=True, blank=True)  # Full name for recipient
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    # Optional map integration fields
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name or ''} - {self.address}, {self.city} ({self.pincode})"

    class Meta:
        verbose_name_plural = "Delivery Addresses"
        ordering = ['-id']


class Order(models.Model):
    """
    Represents a food order placed by a user.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Optional live driver location tracking
    driver_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    driver_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status.upper()} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Represents individual food items within an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} (Order #{self.order.id})"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
