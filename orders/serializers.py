from rest_framework import serializers
from .models import Order, OrderItem
from food.models import FoodItem
from users.models import DeliveryAddress


class OrderItemSerializer(serializers.Serializer):
    food_item = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)
    payment_method = serializers.CharField(default="COD")

    def create(self, validated_data):
        user = self.context['request'].user
        address_id = validated_data["delivery_address_id"]
        items_data = validated_data["items"]

        delivery_address = DeliveryAddress.objects.get(id=address_id)

        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            total_amount=0,
            payment_method=validated_data.get("payment_method", "COD")
        )

        total_price = 0

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

        order.total_amount = total_price
        order.save()

        return order
