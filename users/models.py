from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

# ⭐ USER ROLES
ROLE_CHOICES = (
    ('user', 'User'),
    ('captain', 'Captain'),
)

# ⭐ Custom User Model
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')  # ⭐ NEW ROLE FIELD
    notifications_enabled = models.BooleanField(default=True)

    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return f"{self.email} ({self.role})"

    def set_reset_token(self, token):
        self.reset_token = token
        self.reset_token_expiry = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['reset_token', 'reset_token_expiry'])

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
        self.save(update_fields=['reset_token', 'reset_token_expiry'])


# ⭐ Delivery Address Model
class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    house = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Delivery Address"
        verbose_name_plural = "Delivery Addresses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name}, {self.house}, {self.city}"
