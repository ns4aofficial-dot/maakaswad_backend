from rest_framework import serializers
from .models import Cart, CartItem
from food.models import FoodItem

# ✅ Minimal food item details
class FoodItemMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'price', 'image']  # Added image for cart display

# ✅ CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemMinimalSerializer(read_only=True)
    food_item_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.all(), write_only=True, source='food_item', required=False
    )
    quantity = serializers.IntegerField(required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'food_item', 'food_item_id', 'quantity']
