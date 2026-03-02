from rest_framework import serializers
from .models import Category, FoodItem, Favorite, SupportTicket


# ✅ Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


# ✅ Food Item Serializer
class FoodItemSerializer(serializers.ModelSerializer):

    # 🔥 Allow category selection while creating
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

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

    # 🔥 Automatically assign chef
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["chef"] = request.user
        return super().create(validated_data)


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