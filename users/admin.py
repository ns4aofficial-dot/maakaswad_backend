# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, DeliveryAddress

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ('email', 'username', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'phone')

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'phone', 'user')
    search_fields = ('full_name', 'city', 'phone')
