from django.contrib import admin
from .models import Order, OrderItem, DeliveryAddress


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'delivery_address__city', 'id')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'quantity')
    search_fields = ('order__id', 'food_item__name')
    list_filter = ('food_item__name',)


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'full_address', 'city', 'pincode')
    search_fields = ('user__username', 'city', 'pincode', 'street')
    list_filter = ('city',)

    def full_address(self, obj):
        """Combine street, city, and state into a single address column."""
        return f"{obj.street}, {obj.city}, {obj.state}"
    full_address.short_description = "Address"
