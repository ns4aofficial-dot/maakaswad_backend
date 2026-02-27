from django.db import models
from users.models import User
from food.models import FoodItem


# ==========================================================
# 📍 Delivery Address (Keep as is)
# ==========================================================

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="delivery_addresses")
    full_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name or ''} - {self.address}, {self.city} ({self.pincode})"

    class Meta:
        verbose_name_plural = "Delivery Addresses"
        ordering = ['-id']


# ==========================================================
# 🛒 Order Model (UPDATED FOR CHEF & CAPTAIN)
# ==========================================================

class Order(models.Model):

    STATUS_CHOICES = [
        # Customer side
        ('pending', 'Pending'),

        # Chef side
        ('accepted', 'Accepted'),
        ('preparing', 'Preparing'),
        ('ready_for_pickup', 'Ready for Pickup'),

        # Captain side
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('out_for_delivery', 'Out for Delivery'),

        # Final
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # ⭐ NEW FIELDS
    assigned_chef = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chef_orders",
        limit_choices_to={'role': 'chef'}
    )

    assigned_captain = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captain_orders",
        limit_choices_to={'role': 'captain'}
    )

    delivery_address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Live tracking (Captain)
    driver_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    driver_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.status.upper()}"

    class Meta:
        ordering = ['-created_at']


# ==========================================================
# 🍱 Order Items
# ==========================================================

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} (Order #{self.order.id})"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"