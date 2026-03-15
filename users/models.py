from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone


# -----------------------------------------------------------
# ⭐ Custom User Model
# -----------------------------------------------------------

class User(AbstractUser):

    # -------------------------------------------------------
    # Basic Fields
    # -------------------------------------------------------
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)

    notifications_enabled = models.BooleanField(default=True)

    # -------------------------------------------------------
    # Role System
    # -------------------------------------------------------
    ROLE_CHOICES = (
        ('user', 'User'),
        ('chef', 'Chef'),
        ('captain', 'Captain'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
    null=True
    )

    # -------------------------------------------------------
    # 🧾 Partner Documents
    # -------------------------------------------------------
    aadhaar_number = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    food_license_number = models.CharField(max_length=50, blank=True, null=True)

    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    aadhaar_image = models.ImageField(upload_to='documents/aadhaar/', blank=True, null=True)
    pan_image = models.ImageField(upload_to='documents/pan/', blank=True, null=True)

    documents_submitted = models.BooleanField(default=False)

    # -------------------------------------------------------
    # 💰 Partner Approval & Payment
    # -------------------------------------------------------
    registration_paid = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # -------------------------------------------------------
    # ⭐ Partner Activity & Earnings
    # -------------------------------------------------------
    is_online = models.BooleanField(default=False)

    total_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    rating = models.FloatField(default=0.0)

    # -------------------------------------------------------
    # Captain Specific Fields
    # -------------------------------------------------------
    captain_id = models.CharField(max_length=20, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    # -------------------------------------------------------
    # Reset Password
    # -------------------------------------------------------
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    # -------------------------------------------------------
    # Django Auth Config
    # -------------------------------------------------------
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return f"{self.email} ({self.role})"

    # -------------------------------------------------------
    # Password Reset
    # -------------------------------------------------------
    def set_reset_token(self, token):
        self.reset_token = token
        self.reset_token_expiry = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['reset_token', 'reset_token_expiry'])

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
        self.save(update_fields=['reset_token', 'reset_token_expiry'])

    # -------------------------------------------------------
    # Helper Properties
    # -------------------------------------------------------
    @property
    def is_partner(self):
        return self.role in ['chef', 'captain']

    @property
    def can_login_partner_app(self):
        return (
            self.is_partner and
            self.registration_paid and
            self.is_approved
        )


# -----------------------------------------------------------
# ⭐ Delivery Address
# -----------------------------------------------------------

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

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Delivery Address"
        verbose_name_plural = "Delivery Addresses"