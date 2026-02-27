from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DeliveryAddress

User = get_user_model()


# ===========================================================
# ✅ USER PROFILE SERIALIZER
# ===========================================================

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


# ===========================================================
# ✅ REGISTRATION SERIALIZER (Updated for Chef & Captain)
# ===========================================================

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default="user"
    )

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

    def validate(self, data):
        role = data.get("role")

        # Captain validation
        if role == "captain":
            if not data.get("captain_id"):
                raise serializers.ValidationError({
                    "captain_id": "Captain ID is required for captain role."
                })
            if not data.get("vehicle_number"):
                raise serializers.ValidationError({
                    "vehicle_number": "Vehicle number is required for captain role."
                })
            if not data.get("city"):
                raise serializers.ValidationError({
                    "city": "City is required for captain role."
                })

        return data

    def create(self, validated_data):
        role = validated_data.pop("role", "user")
        captain_id = validated_data.pop("captain_id", None)
        vehicle_number = validated_data.pop("vehicle_number", None)
        city = validated_data.pop("city", None)

        user = User.objects.create_user(
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


# ===========================================================
# ✅ DELIVERY ADDRESS SERIALIZER
# ===========================================================

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


# ===========================================================
# ✅ NOTIFICATION SETTINGS SERIALIZER
# ===========================================================

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notifications_enabled']