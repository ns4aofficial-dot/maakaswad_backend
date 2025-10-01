from rest_framework import serializers
from .models import Category, FoodItem, Favorite, SupportTicket

# ✅ Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)  # Ensure image URL is included

    class Meta:
        model = Category
        fields = ['id', 'name', 'image']  # id, name, and image for frontend icons

# ✅ Food Item Serializer
class FoodItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(read_only=True)  # Link category by ID

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
