from django.urls import path
from django.views.decorators.http import require_GET
from django.http import JsonResponse

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    DeliveryAddressListCreateView,
    DeliveryAddressDetailView,
    NotificationSettingsView,
    ForgotPasswordView,
    ResetPasswordView,
    DeleteAccountView,
    SocialLoginView,
)

@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path("health/", health_check, name="health"),

    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Google Social Login
    path("social/", SocialLoginView.as_view(), name="social-login"),

    # Profile
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("notifications/", NotificationSettingsView.as_view(), name="notifications"),

    # Delivery Address
    path("addresses/", DeliveryAddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", DeliveryAddressDetailView.as_view(), name="address-detail"),

    # Password management
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    # Delete Account
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
]
