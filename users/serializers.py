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
            'role'       # ⭐ ADDED ROLE
        ]
        read_only_fields = ['id', 'username', 'email', 'role']


# ✅ REGISTRATION SERIALIZER (Supports user/captain role)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.CharField(required=False, default="user")  # ⭐ NEW

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'role']

    def create(self, validated_data):
        role = validated_data.pop("role", "user")

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )

        # ⭐ Set role explicitly
        user.role = role
        user.save(update_fields=['role'])

        return user


# ✅ DELIVERY ADDRESS SERIALIZER (matches your updated model)
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

    # Automatically assign logged-in user
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        validated_data['user'] = user
        return super().create(validated_data)


# ✅ NOTIFICATION SETTINGS SERIALIZER
class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notifications_enabled']
