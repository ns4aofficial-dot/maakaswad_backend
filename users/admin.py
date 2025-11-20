from django.contrib import admin
from .models import User, DeliveryAddress


# ------------------------------
# USER ADMIN
# ------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email", "phone",
        "role", "captain_id", "vehicle_number", "city",
        "notifications_enabled",
    )

    list_filter = ("role", "city", "notifications_enabled")
    search_fields = ("username", "email", "phone", "captain_id", "vehicle_number")

    fieldsets = (
        ("User Info", {
            "fields": ("username", "email", "phone", "password")
        }),
        ("Roles", {
            "fields": ("role",)
        }),
        ("Captain Details", {
            "fields": ("captain_id", "vehicle_number", "city"),
            "classes": ("collapse",)
        }),
        ("Settings", {
            "fields": ("notifications_enabled",)
        }),
    )

    readonly_fields = ("password",)


# ------------------------------
# DELIVERY ADDRESS ADMIN
# ------------------------------
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "full_name", "city",
        "pincode", "phone", "default", "created_at"
    )

    list_filter = ("city", "default")
    search_fields = ("full_name", "city", "pincode", "phone", "house", "street")
