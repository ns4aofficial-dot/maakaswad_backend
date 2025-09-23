from rest_framework import serializers
from .models import DeliveryAddress, Order, OrderItem
from food.models import FoodItem

# ✅ Delivery Address Serializer
class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = [
            'id',
            'full_name',
            'address',
            'city',
            'pincode',
            'phone',
            'latitude',
            'longitude',
        ]

# ✅ Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_price = serializers.DecimalField(
        source='food_item.price', max_digits=8, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'food_item_name', 'food_item_price', 'quantity']

# ✅ Main Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'delivery_address',
            'created_at',
            'status',
            'total_amount',
            'driver_latitude',
            'driver_longitude',
            'items',
        ]

# ✅ PlaceOrderItemSerializer
class PlaceOrderItemSerializer(serializers.Serializer):
    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.filter(is_available=True))
    quantity = serializers.IntegerField(min_value=1)

# ✅ PlaceOrderSerializer
class PlaceOrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = PlaceOrderItemSerializer(many=True)

    def validate(self, attrs):
        # Validate delivery address belongs to user
        address_id = attrs.get('delivery_address_id')
        user = self.context['request'].user
        try:
            address = DeliveryAddress.objects.get(id=address_id, user=user)
        except DeliveryAddress.DoesNotExist:
            raise serializers.ValidationError({
                'delivery_address_id': ['Invalid delivery address for this user.']
            })
        attrs['delivery_address'] = address
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        address = validated_data['delivery_address']
        items_data = validated_data['items']

        total_amount = 0

        # ✅ Create order
        order = Order.objects.create(
            user=user,
            delivery_address=address,
            total_amount=0,
            status='pending'
        )

        # ✅ Create order items and calculate total
        for item in items_data:
            food = item['food_item']
            quantity = item['quantity']
            OrderItem.objects.create(order=order, food_item=food, quantity=quantity)
            total_amount += food.price * quantity

        # ✅ Update order total
        order.total_amount = total_amount
        order.save()

        return order
