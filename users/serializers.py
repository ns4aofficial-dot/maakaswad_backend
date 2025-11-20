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


# ✅ DELIVERY ADDRESS SERIALIZER (UPDATED)
class DeliveryAddressSerializer(serializers.ModelSerializer):
    house = serializers.CharField(write_only=True, required=True)
    street = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = DeliveryAddress
        fields = ['id', 'user', 'full_name', 'phone', 'house', 'street', 'address',
                  'landmark', 'city', 'state', 'pincode', 'created_at']
        read_only_fields = ['id', 'user', 'address', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Combine house + street into address field
        house = validated_data.pop('house', '')
        street = validated_data.pop('street', '')
        validated_data['address'] = f"{house}, {street}".strip(', ')
        validated_data['user'] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Combine house + street for update
        house = validated_data.pop('house', None)
        street = validated_data.pop('street', None)
        if house or street:
            h = house if house is not None else instance.address.split(',')[0]
            s = street if street is not None else instance.address.split(',')[1] if ',' in instance.address else ''
            instance.address = f"{h}, {s}".strip(', ')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ✅ NOTIFICATION SETTINGS SERIALIZER
class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notifications_enabled']
