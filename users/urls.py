from django.urls import path
from django.views.decorators.http import require_GET
from django.http import JsonResponse

from .views import (
    RegisterView,
    LoginView,
    PartnerLoginView,
    PartnerRegisterView,
    UserProfileView,
    DeliveryAddressListCreateView,
    DeliveryAddressDetailView,
    ForgotPasswordView,
    ResetPasswordView,
    DeleteAccountView,
    SocialLoginView,
    UpdatePartnerRoleView,
    GetPartnerRoleView,
)

# ==========================================================
# 🟢 Health Check
# ==========================================================

@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

# ==========================================================
# 🟢 URL Patterns
# ==========================================================

urlpatterns = [

    # System
    path("health/", health_check),

    # Customer Authentication
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),

    # Partner Authentication
    path("partner-register/", PartnerRegisterView.as_view()),
    path("partner-login/", PartnerLoginView.as_view()),
    path("partner/update-role/", UpdatePartnerRoleView.as_view()),
    path("partner/get-role/", GetPartnerRoleView.as_view()),

    # Social Login
    path("social/", SocialLoginView.as_view()),

    # Profile
    path("profile/", UserProfileView.as_view()),

    # Delivery Address
    path("addresses/", DeliveryAddressListCreateView.as_view()),
    path("addresses/<int:pk>/", DeliveryAddressDetailView.as_view()),

    # Password
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),

    # Account
    path("delete-account/", DeleteAccountView.as_view()),
]