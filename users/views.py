from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser

import traceback
import requests

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DeliveryAddressSerializer,
    NotificationSettingsSerializer,
    PartnerDocumentSerializer   # ✅ NEW
)
from .models import DeliveryAddress

User = get_user_model()

# ==========================================================
# ✅ JWT GENERATOR
# ==========================================================
def generate_jwt(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data
    }


# ==========================================================
# 🟢 HEALTH CHECK
# ==========================================================
@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "ok"})


# ==========================================================
# 🟢 GOOGLE SOCIAL LOGIN
# ==========================================================
class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        provider = request.data.get("provider")
        access_token = request.data.get("access_token")

        if provider != "google":
            return Response({"detail": "Only Google login supported"}, status=400)

        if not access_token:
            return Response({"detail": "Missing Google access token"}, status=400)

        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                return Response({"detail": "Invalid Google token"}, status=400)

            data = response.json()
            email = data.get("email")
            name = data.get("name") or email.split("@")[0]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": name,
                    "role": "user",
                    "is_approved": True
                }
            )

            if user.role != "user":
                return Response({"detail": "Partner accounts cannot login here"}, status=403)

            return Response(generate_jwt(user), status=200)

        except Exception:
            traceback.print_exc()
            return Response({"detail": "Google login failed"}, status=500)


# ==========================================================
# 🟢 CUSTOMER REGISTER
# ==========================================================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.role = "user"
            user.is_approved = True
            user.registration_paid = True
            user.save()
            return Response(generate_jwt(user), status=201)

        return Response(serializer.errors, status=400)


# ==========================================================
# 🔵 PARTNER REGISTER
# ==========================================================
class PartnerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.role = "chef"
            user.is_approved = False
            user.registration_paid = False
            user.save()
            return Response(generate_jwt(user), status=201)

        return Response(serializer.errors, status=400)


# ==========================================================
# 🟢 CUSTOMER LOGIN
# ==========================================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"detail": "Missing credentials"}, status=400)

        user = User.objects.filter(
            Q(email__iexact=identifier) |
            Q(phone=identifier) |
            Q(username__iexact=identifier)
        ).first()

        if not user:
            return Response({"detail": "User not found"}, status=404)

        if not user.check_password(password):
            return Response({"detail": "Invalid password"}, status=401)

        if user.role != "user":
            return Response({"detail": "Partner accounts not allowed here"}, status=403)

        return Response(generate_jwt(user), status=200)


# ==========================================================
# 🔵 PARTNER LOGIN
# ==========================================================
class PartnerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"detail": "Missing credentials"}, status=400)

        user = User.objects.filter(
            Q(email__iexact=identifier) |
            Q(phone=identifier) |
            Q(username__iexact=identifier)
        ).first()

        if not user:
            return Response({"detail": "User not found"}, status=404)

        if not user.check_password(password):
            return Response({"detail": "Invalid password"}, status=401)

        if user.role not in ["chef", "captain"]:
            return Response({"detail": "Not a partner account"}, status=403)

        if not user.registration_paid:
            return Response({"detail": "Registration fee not paid"}, status=403)

        if not user.is_approved:
            return Response({"detail": "Waiting for admin approval"}, status=403)

        return Response(generate_jwt(user), status=200)


# ==========================================================
# 🔵 UPDATE ROLE
# ==========================================================
class UpdatePartnerRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = request.data.get("role")

        if role not in ["chef", "captain"]:
            return Response({"detail": "Invalid role"}, status=400)

        user = request.user
        user.role = role
        user.is_approved = False
        user.registration_paid = False
        user.save()

        return Response({"detail": "Role updated. Submit documents."})


# ==========================================================
# 🔥 PARTNER DOCUMENT SUBMISSION
# ==========================================================
class PartnerDocumentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = PartnerDocumentSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Documents submitted successfully"},
                status=200
            )

        return Response(serializer.errors, status=400)


# ==========================================================
# 🔵 GET ROLE STATUS
# ==========================================================
class GetPartnerRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "role": user.role,
            "is_approved": user.is_approved,
            "registration_paid": user.registration_paid
        })


# ==========================================================
# 🟢 PROFILE
# ==========================================================
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# ==========================================================
# 🟢 DELIVERY ADDRESS
# ==========================================================
class DeliveryAddressListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeliveryAddressDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


# ==========================================================
# 🟢 DELETE ACCOUNT
# ==========================================================
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.delete()
        return Response({"detail": "Account deleted successfully"})


# ==========================================================
# 🟢 FORGOT PASSWORD
# ==========================================================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"detail": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
            token = get_random_string(32)
            user.set_reset_token(token)

            send_mail(
                subject="Password Reset",
                message=f"Reset token: {token}",
                from_email="noreply@maakaswad.com",
                recipient_list=[email],
            )

            return Response({"detail": "Reset token sent"})

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)


# ==========================================================
# 🟢 RESET PASSWORD
# ==========================================================
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([email, token, new_password]):
            return Response({"detail": "All fields required"}, status=400)

        try:
            user = User.objects.get(email=email)

            if user.reset_token != token or user.reset_token_expiry < timezone.now():
                return Response({"detail": "Invalid or expired token"}, status=400)

            user.set_password(new_password)
            user.clear_reset_token()
            user.save()

            return Response({"detail": "Password reset successful"})

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)