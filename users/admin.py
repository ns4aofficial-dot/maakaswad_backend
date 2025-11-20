from django.contrib import admin
from .models import User, DeliveryAddress


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "phone",
        "role",
        "captain_id",
        "vehicle_number",
        "city",
        "notifications_enabled",
    )
    list_filter = ("role", "city", "notifications_enabled")
    search_fields = (
        "username",
        "email",
        "phone",
        "captain_id",
        "vehicle_number",
        "city",
    )


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "phone",
        "pincode",
        "city",
        "state",
        "default",
        "created_at",
    )
    list_filter = ("city", "state", "default")
    search_fields = ("full_name", "phone", "city", "state", "pincode")
