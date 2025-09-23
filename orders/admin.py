from django.contrib import admin
from .models import Order, OrderItem, DeliveryAddress

# Inline for order items in Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('food_item', 'quantity')
    # Display the food item price if you want
    # You can define a method on OrderItem to get price if needed

# Order admin with inline order items
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    readonly_fields = ('driver_latitude', 'driver_longitude')

# Delivery Address admin
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'address', 'city', 'pincode', 'phone')
    search_fields = ('full_name', 'user__username', 'city', 'pincode')
    ordering = ('-id',)

# Optionally register OrderItem separately if you want to manage it individually
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'food_item', 'quantity')
    search_fields = ('order__id', 'food_item__name')
