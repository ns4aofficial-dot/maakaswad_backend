from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, DeliveryAddress


# ✅ USER PROFILE SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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


# ✅ REGISTRATION SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    # ⭐ Extra fields for Captain
    role = serializers.CharField(required=False, default="user")
    captain_id = serializers.CharField(required=False, allow_blank=True)
    vehicle_number = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
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

        # create base user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )

        # assign role + extra details
        user.role = role

        if role == "captain":
            user.captain_id = captain_id
            user.vehicle_number = vehicle_number
            user.city = city

        user.save()
        return user


# ✅ DELIVERY ADDRESS SERIALIZER
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


# ✅ NOTIFICATION SETTINGS SERIALIZER
class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notifications_enabled']
