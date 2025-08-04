from rest_framework import serializers
from .models import Category, FoodItem, Order, OrderItem, Favorite, SupportTicket


# ✅ Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


# ✅ Food Item Serializer
class FoodItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id',
            'name',
            'description',
            'price',
            'image',
            'category',
            'is_available',
        ]


# ✅ Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity', 'price']


# ✅ Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_price',
            'created_at',
            'items',
        ]


# ✅ Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'food_item', 'created_at']


# ✅ Support Ticket Serializer
class SupportTicketSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SupportTicket
        fields = ['id', 'user', 'message', 'status', 'created_at']
