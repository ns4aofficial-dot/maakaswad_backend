# users/serializers.py
from rest_framework import serializers
from .models import User, DeliveryAddress  # DeliveryAddress defined below in same app or separate app
from django.contrib.auth import get_user_model

UserModel = get_user_model()

# -----------------------
# User Serializer
# -----------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'id',
            'username',
            'email',
            'phone',
            'notifications_enabled',
            'role',
            'captain_id',
            'vehicle_number',
            'city',
        ]
        read_only_fields = ['id', 'username', 'email', 'role']


# -----------------------
# Register Serializer
# -----------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.CharField(required=False, default="user")
    captain_id = serializers.CharField(required=False, allow_blank=True)
    vehicle_number = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserModel
        fields = [
            'username',
            'email',
            'password',
            'phone',
            'role',
            'captain_id',
            'vehicle_number',
            'city'
        ]

    def create(self, validated_data):
        role = validated_data.pop("role", "user")
        captain_id = validated_data.pop("captain_id", None)
        vehicle_number = validated_data.pop("vehicle_number", None)
        city = validated_data.pop("city", None)

        user = UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )

        user.role = role
        if role == "captain":
            user.captain_id = captain_id
            user.vehicle_number = vehicle_number
            user.city = city

        user.save()
        return user


# -----------------------
# Delivery Address Serializer
# -----------------------
class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = [
            'id',
            'full_name',
            'phone',
            'pincode',
            'house',
            'street',
            'landmark',
            'city',
            'state',
            'default',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------
# Notification Settings Serializer
# -----------------------
class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['notifications_enabled']
