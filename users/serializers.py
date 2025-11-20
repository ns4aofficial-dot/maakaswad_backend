from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, DeliveryAddress


# ✅ USER PROFILE SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'notifications_enabled']
        read_only_fields = ['id', 'username', 'email']


# ✅ REGISTRATION SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )


# ✅ DELIVERY ADDRESS SERIALIZER
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
        read_only_fields = ['id']

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
