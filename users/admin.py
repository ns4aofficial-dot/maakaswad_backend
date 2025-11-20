from django.contrib import admin
from .models import User
from .models import DeliveryAddress

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'role', 'captain_id', 'vehicle_number', 'city')
    list_filter = ('role', 'city')
    search_fields = ('username', 'email', 'phone', 'captain_id')

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone', 'city', 'state', 'pincode', 'default')
    search_fields = ('full_name', 'phone', 'city')
    list_filter = ('city', 'state', 'default')
