# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)

    notifications_enabled = models.BooleanField(default=True)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('captain', 'Captain'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Captain extra fields
    captain_id = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # password reset
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return self.email

    def set_reset_token(self, token, minutes_valid: int = 15):
        self.reset_token = token
        self.reset_token_expiry = timezone.now() + timedelta(minutes=minutes_valid)
        self.save(update_fields=['reset_token', 'reset_token_expiry'])

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
        self.save(update_fields=['reset_token', 'reset_token_expiry'])
