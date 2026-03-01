import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from rest_framework import serializers

from .models import DeliveryAddress, Order, OrderItem
from food.models import FoodItem

logger = logging.getLogger(__name__)


# ==========================================================
# 📍 Delivery Address Serializer
# ==========================================================
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
            'longitude'
        ]


# ==========================================================
# 🍱 Order Item Serializer
# ==========================================================
class OrderItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_price = serializers.DecimalField(
        source='food_item.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'food_item',
            'food_item_name',
            'food_item_price',
            'quantity'
        ]


# ==========================================================
# 🛒 Order List Serializer
# ==========================================================
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)

    user = serializers.StringRelatedField(read_only=True)
    assigned_chef = serializers.StringRelatedField(read_only=True)
    assigned_captain = serializers.StringRelatedField(read_only=True)

    driver_location = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'assigned_chef',
            'assigned_captain',
            'delivery_address',
            'created_at',
            'status',
            'total_amount',
            'driver_location',
            'destination',
            'items'
        ]

    def get_driver_location(self, obj):
        if obj.driver_latitude and obj.driver_longitude:
            return {
                "latitude": float(obj.driver_latitude),
                "longitude": float(obj.driver_longitude)
            }
        return None

    def get_destination(self, obj):
        if obj.delivery_address and obj.delivery_address.latitude and obj.delivery_address.longitude:
            return {
                "latitude": float(obj.delivery_address.latitude),
                "longitude": float(obj.delivery_address.longitude)
            }
        return None


# ==========================================================
# 📄 Order Detail Serializer
# ==========================================================
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)

    user = serializers.StringRelatedField(read_only=True)
    assigned_chef = serializers.StringRelatedField(read_only=True)
    assigned_captain = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'assigned_chef',
            'assigned_captain',
            'delivery_address',
            'created_at',
            'status',
            'total_amount',
            'driver_latitude',
            'driver_longitude',
            'items'
        ]


# ==========================================================
# 📝 Place Order
# ==========================================================
class PlaceOrderItemSerializer(serializers.Serializer):
    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate_food_item(self, food_item):
        if not food_item.is_available:
            raise serializers.ValidationError("This food item is not available.")
        return food_item


class PlaceOrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = PlaceOrderItemSerializer(many=True)

    def validate(self, attrs):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        try:
            address = DeliveryAddress.objects.get(
                id=attrs.get('delivery_address_id'),
                user=request.user
            )
        except DeliveryAddress.DoesNotExist:
            raise serializers.ValidationError("Invalid delivery address.")

        attrs['delivery_address'] = address
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        address = validated_data['delivery_address']
        items_data = validated_data['items']

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                delivery_address=address,
                total_amount=Decimal('0.00'),
                status='pending'
            )

            total_price = Decimal('0.00')

            for item in items_data:
                food = item['food_item']
                quantity = int(item['quantity'])

                OrderItem.objects.create(
                    order=order,
                    food_item=food,
                    quantity=quantity
                )

                try:
                    price = Decimal(str(food.price))
                except (InvalidOperation, TypeError, ValueError):
                    logger.error(f"Invalid price for food item {food.id}")
                    price = Decimal('0.00')

                total_price += price * Decimal(quantity)

            order.total_amount = total_price.quantize(Decimal("0.01"))
            order.save(update_fields=["total_amount"])

        return order


# ==========================================================
# 👩‍🍳 Chef Status Update
# ==========================================================
class ChefStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed = ['accepted', 'preparing', 'ready_for_pickup']
        if value not in allowed:
            raise serializers.ValidationError("Invalid status for chef.")
        return value


# ==========================================================
# 🚴 Captain Status Update
# ==========================================================
class CaptainStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed = ['assigned', 'picked_up', 'out_for_delivery', 'delivered']
        if value not in allowed:
            raise serializers.ValidationError("Invalid status for captain.")
        return value


# ==========================================================
# 📍 Driver Location Update
# ==========================================================
class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['driver_latitude', 'driver_longitude']

    def validate(self, attrs):
        lat = attrs.get("driver_latitude")
        lon = attrs.get("driver_longitude")

        if lat is None or lon is None:
            raise serializers.ValidationError("Latitude and Longitude required.")

        if not (-90 <= lat <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")

        if not (-180 <= lon <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")

        return attrs