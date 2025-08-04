from django.db import models
from users.models import User
from food.models import FoodItem

# Parent Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username} (ID: {self.id})"

# Individual Items in the Cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'food_item')

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} in Cart ID {self.cart.id}"
