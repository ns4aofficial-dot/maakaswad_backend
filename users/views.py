from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback
import requests  # ⭐ REQUIRED FOR GOOGLE TOKEN VERIFY

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DeliveryAddressSerializer,
    NotificationSettingsSerializer
)
from .models import DeliveryAddress

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken  # ⭐ JWT TOKEN

User = get_user_model()


# =============================
# ⭐ JWT Generator
# =============================
def generate_jwt(user):
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data
    }


# =============================
# 🟢 Health Check
# =============================
@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "ok"})


# =============================
# 🟢 Social Login (GOOGLE)
# =============================
class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        provider = request.data.get("provider")
        access_token = request.data.get("access_token")

        if provider != "google":
            return Response({"detail": "Only Google supported now"}, status=400)

        # ⭐ Verify Google Token
        google_url = "https://oauth2.googleapis.com/tokeninfo"
        resp = requests.get(google_url, params={"id_token": access_token})

        if resp.status_code != 200:
            return Response({"detail": "Invalid Google token"}, status=400)

        data = resp.json()
        email = data.get("email")
        name = data.get("name") or email.split("@")[0]

        if not email:
            return Response({"detail": "Google login failed"}, status=400)

        # ⭐ Create/Get User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": name, "role": "user"}
        )

        # ⭐ Return JWT Token
        return Response(generate_jwt(user), status=200)


# =============================
# 🟢 Register
# =============================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data.copy()
            role = data.get("role", "user")

            serializer = RegisterSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()

                # ⭐ Return JWT
                return Response(generate_jwt(user), status=201)

            return Response(serializer.errors, status=400)

        except Exception:
            traceback.print_exc()
            return Response({'detail': 'Server error in Register'}, status=500)


# =============================
# 🟢 Login (username/email/phone)
# =============================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            identifier = request.data.get('identifier')
            password = request.data.get('password')

            if not identifier or not password:
                return Response({'detail': 'Missing credentials'}, status=400)

            user = User.objects.filter(
                Q(email__iexact=identifier) |
                Q(phone=identifier) |
                Q(username__iexact=identifier)
            ).first()

            if not user:
                return Response({'detail': 'User not found'}, status=404)

            if not user.check_password(password):
                return Response({'detail': 'Invalid password'}, status=401)

            return Response(generate_jwt(user), status=200)

        except Exception:
            traceback.print_exc()
            return Response({'detail': 'Server error in Login'}, status=500)


# =============================
# 🟢 Logout (JWT doesn't need delete)
# =============================
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({'detail': 'Logged out successfully'}, status=200)


# =============================
# 🟢 User Profile
# =============================
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=200)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


# =============================
# 🟢 Notification Settings
# =============================
class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = NotificationSettingsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


# =============================
# 🟢 Delivery Address
# =============================
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


# =============================
# 🟢 Delete Account
# =============================
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        DeliveryAddress.objects.filter(user=user).delete()
        user.delete()
        return Response({"detail": "Account deleted successfully"}, status=200)


# =============================
# 🟢 Forgot Password
# =============================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'detail': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
            token = get_random_string(32)
            user.set_reset_token(token)

            send_mail(
                subject="Password Reset Request",
                message=f"Use this token to reset your password: {token}",
                from_email="noreply@maakaswad.com",
                recipient_list=[email],
            )

            return Response({'detail': 'Reset token sent'}, status=200)

        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)


# =============================
# 🟢 Reset Password
# =============================
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([email, token, new_password]):
            return Response({'detail': 'All fields required'}, status=400)

        try:
            user = User.objects.get(email=email)

            if user.reset_token != token:
                return Response({'detail': 'Invalid or expired token'}, status=400)

            user.set_password(new_password)
            user.clear_reset_token()
            user.save()

            return Response({'detail': 'Password reset successful'}, status=200)

        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
