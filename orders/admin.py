from django.contrib import admin
from .models import Order, OrderItem, DeliveryAddress


# ---------------------------
# ✅ ADMIN ACTIONS
# ---------------------------
@admin.action(description="Accept Selected Orders (Processing)")
def accept_orders(modeladmin, request, queryset):
    queryset.update(status="processing")


@admin.action(description="Mark as Out for Delivery")
def mark_out_for_delivery(modeladmin, request, queryset):
    queryset.update(status="out_for_delivery")


@admin.action(description="Mark as Delivered")
def mark_delivered(modeladmin, request, queryset):
    queryset.update(status="delivered")


@admin.action(description="Reject / Cancel Selected Orders")
def reject_orders(modeladmin, request, queryset):
    queryset.update(status="cancelled")


# ---------------------------
# ✅ ORDER ADMIN
# ---------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'delivery_address__city', 'id')
    ordering = ('-created_at',)

    # ⭐ Add action buttons
    actions = [
        accept_orders,
        mark_out_for_delivery,
        mark_delivered,
        reject_orders
    ]


# ---------------------------
# ✅ ORDER ITEM ADMIN
# ---------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'quantity')
    search_fields = ('order__id', 'food_item__name')
    list_filter = ('food_item__name',)


# ---------------------------
# ✅ DELIVERY ADDRESS ADMIN
# ---------------------------
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address', 'city', 'pincode')
    search_fields = ('user__username', 'city', 'pincode', 'address')
    list_filter = ('city',)
