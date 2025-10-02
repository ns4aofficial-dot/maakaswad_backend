import logging
from rest_framework import serializers
from .models import DeliveryAddress, Order, OrderItem
from food.models import FoodItem

logger = logging.getLogger(__name__)

# --- Delivery Address Serializer ---
class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = [
            'id', 'full_name', 'address', 'city', 'pincode', 'phone', 'latitude', 'longitude'
        ]


# --- Order Item Serializer ---
class OrderItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_price = serializers.DecimalField(
        source='food_item.price', max_digits=8, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'food_item_name', 'food_item_price', 'quantity']


# --- Order Serializer ---
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'delivery_address', 'created_at', 'status',
            'total_amount', 'driver_latitude', 'driver_longitude', 'items'
        ]

    def get_delivery_address(self, obj):
        if obj.delivery_address:
            return DeliveryAddressSerializer(obj.delivery_address).data
        return None


# --- Place Order Item Serializer ---
class PlaceOrderItemSerializer(serializers.Serializer):
    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate_food_item(self, food_item):
        if not food_item.is_available:
            raise serializers.ValidationError("This food item is not available.")
        return food_item


# --- Place Order Serializer ---
class PlaceOrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = PlaceOrderItemSerializer(many=True)

    def validate(self, attrs):
        request = self.context.get('request')
        address_id = attrs.get('delivery_address_id')

        if not address_id:
            raise serializers.ValidationError({
                'delivery_address_id': ['This field is required.']
            })

        try:
            address = DeliveryAddress.objects.get(id=address_id, user=request.user)
        except DeliveryAddress.DoesNotExist:
            raise serializers.ValidationError({
                'delivery_address_id': ['Invalid delivery address for this user.']
            })

        attrs['delivery_address'] = address
        return attrs

    def create(self, validated_data):
        logger.info(f"Creating order with data: {validated_data}")
        user = self.context['request'].user
        address = validated_data['delivery_address']
        items_data = validated_data['items']

        total_price = 0

        order = Order.objects.create(
            user=user,
            delivery_address=address,
            total_amount=0,
            status='pending'
        )

        logger.info(f"Created order #{order.id}")

        for item in items_data:
            food = item['food_item']
            quantity = item['quantity']

            logger.info(f"Adding item: {food.name} x {quantity}")

            OrderItem.objects.create(
                order=order,
                food_item=food,
                quantity=quantity
            )

            total_price += food.price * quantity

        order.total_amount = total_price
        order.save()

        logger.info(f"Order #{order.id} finalized with total: {total_price}")

        return order


# --- Driver Location Update Serializer ---
class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['driver_latitude', 'driver_longitude']

    def validate(self, attrs):
        lat = attrs.get("driver_latitude")
        lon = attrs.get("driver_longitude")

        if lat is None or lon is None:
            raise serializers.ValidationError("Latitude and Longitude must be provided.")

        if not (-90 <= lat <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")

        if not (-180 <= lon <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")

        return attrs


# --- Accept Order Serializer ---
class AcceptOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value != 'processing':
            raise serializers.ValidationError("Status must be 'processing' to accept an order.")
        return value


# --- Reject Order Serializer ---
class RejectOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value != 'cancelled':
            raise serializers.ValidationError("Status must be 'cancelled' to reject an order.")
        return value
