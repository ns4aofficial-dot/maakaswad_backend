﻿import logging
from rest_framework import serializers
from .models import DeliveryAddress, Order, OrderItem
from food.models import FoodItem

logger = logging.getLogger(__name__)


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = [
            'id', 'full_name', 'address', 'city', 'pincode', 'phone',
            'latitude', 'longitude'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_price = serializers.DecimalField(
        source='food_item.price', max_digits=8, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'food_item_name', 'food_item_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    # New fields for tracking
    driver_location = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'delivery_address', 'created_at', 'status',
            'total_amount', 'driver_location', 'destination', 'items'
        ]

    def get_driver_location(self, obj):
        return {
            "latitude": obj.driver_latitude or None,
            "longitude": obj.driver_longitude or None
        }

    def get_destination(self, obj):
        if obj.delivery_address:
            return {
                "latitude": obj.delivery_address.latitude or None,
                "longitude": obj.delivery_address.longitude or None
            }
        return None


class PlaceOrderItemSerializer(serializers.Serializer):
    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate_food_item(self, food_item):
        if not food_item.is_available:
            logger.warning(f"Food item {food_item.id} is not available")
            raise serializers.ValidationError("This food item is not available.")
        return food_item


class PlaceOrderSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField()
    items = PlaceOrderItemSerializer(many=True)

    def validate(self, attrs):
        request = self.context.get('request')
        address_id = attrs.get('delivery_address_id')

        if not address_id:
            logger.error("Missing delivery_address_id in order request")
            raise serializers.ValidationError({
                'delivery_address_id': ['This field is required.']
            })

        try:
            address = DeliveryAddress.objects.get(id=address_id, user=request.user)
        except DeliveryAddress.DoesNotExist:
            logger.error(f"Invalid delivery address {address_id} for user {request.user}")
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

        order = Order.objects.create(
            user=user,
            delivery_address=address,
            total_amount=0,
            status='pending'
        )

        logger.info(f"Created order #{order.id}")

        total_price = 0
        for item in items_data:
            food = item['food_item']
            quantity = item['quantity']

            logger.info(f"Adding item {food.id} ({food.name}) x {quantity}")

            OrderItem.objects.create(
                order=order,
                food_item=food,
                quantity=quantity
            )

            total_price += float(food.price) * quantity

        order.total_amount = total_price
        order.save()

        logger.info(f"Order #{order.id} finalized with total: {total_price}")
        return order


class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['driver_latitude', 'driver_longitude']

    def validate(self, attrs):
        lat = attrs.get("driver_latitude")
        lon = attrs.get("driver_longitude")

        if lat is None or lon is None:
            logger.error("Latitude or longitude missing in driver location update")
            raise serializers.ValidationError("Latitude and Longitude must be provided.")

        if not (-90 <= lat <= 90):
            logger.error(f"Invalid latitude value: {lat}")
            raise serializers.ValidationError("Latitude must be between -90 and 90.")

        if not (-180 <= lon <= 180):
            logger.error(f"Invalid longitude value: {lon}")
            raise serializers.ValidationError("Longitude must be between -180 and 180.")

        return attrs


class AcceptOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value != 'processing':
            logger.error(f"Invalid status value for accept: {value}")
            raise serializers.ValidationError("Status must be 'processing' to accept an order.")
        return value


class RejectOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value != 'cancelled':
            logger.error(f"Invalid status value for reject: {value}")
            raise serializers.ValidationError("Status must be 'cancelled' to reject an order.")
        return value
