from rest_framework import serializers
from .models import Order, OrderItem
from food.models import FoodItem
from users.models import DeliveryAddress


# ------------------------------
# Order Item Serializer
# ------------------------------
class OrderItemSerializer(serializers.Serializer):
    food_item = serializers.IntegerField()
    quantity = serializers.IntegerField()


# ------------------------------
# Create Order Serializer
# ------------------------------
class OrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)
    payment_method = serializers.CharField(default="COD")

    def create(self, validated_data):
        user = self.context['request'].user
        address_id = validated_data["delivery_address_id"]
        items_data = validated_data["items"]

        delivery_address = DeliveryAddress.objects.get(id=address_id)

        # Create order
        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            total_amount=0,
            payment_method=validated_data.get("payment_method", "COD")
        )

        total_price = 0

        # Add items
        for item_data in items_data:
            food = FoodItem.objects.get(id=item_data["food_item"])
            quantity = item_data["quantity"]
            price = food.price * quantity

            OrderItem.objects.create(
                order=order,
                food_item=food,
                quantity=quantity,
                price=price
            )

            total_price += price

        # Update order total
        order.total_amount = total_price
        order.save()

        return order


# ------------------------------
# Order Item Detail (Read-Only)
# ------------------------------
class OrderItemDetailSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source="food_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "food_item", "food_item_name", "quantity", "price"]


# ------------------------------
# Order Detail Serializer (Fix missing import)
# ------------------------------
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_address",
            "total_amount",
            "payment_method",
            "status",
            "created_at",
            "updated_at",
            "items",
        ]


# ------------------------------
# Order List Serializer
# ------------------------------
class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "total_amount", "status", "created_at"]
