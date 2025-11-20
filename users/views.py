from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DeliveryAddressSerializer,
    NotificationSettingsSerializer
)
from .models import DeliveryAddress

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

User = get_user_model()


# 🟢 Health Check
@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "ok"})


# 🟢 Register (Supports role=user/captain)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data.copy()
            role = data.get("role", "user")

            # 🔥 Captain Specific Validation
            if role == "captain":
                required = ["captain_id", "vehicle_number", "city"]
                missing = [f for f in required if not data.get(f)]
                if missing:
                    return Response(
                        {"detail": f"Missing fields for captain: {', '.join(missing)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = RegisterSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()  # serializer saves role too

                if role == "captain":
                    user.captain_id = data.get("captain_id")
                    user.vehicle_number = data.get("vehicle_number")
                    user.city = data.get("city")
                    user.save(update_fields=["captain_id", "vehicle_number", "city"])

                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'role': user.role,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            traceback.print_exc()
            return Response({'detail': 'Server error in Register'}, status=500)


# 🟢 Login with ROLE returned
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            identifier = request.data.get('identifier')
            password = request.data.get('password')

            if not identifier or not password:
                return Response({'detail': 'Please provide identifier and password'}, status=400)

            user = User.objects.filter(
                Q(email__iexact=identifier) |
                Q(phone=identifier) |
                Q(username__iexact=identifier)
            ).first()

            if not user:
                return Response({'detail': 'User not found'}, status=404)

            if not user.check_password(password):
                return Response({'detail': 'Invalid password'}, status=401)

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'role': user.role,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'notifications_enabled': user.notifications_enabled,
                    'role': user.role,
                }
            }, status=200)

        except Exception:
            traceback.print_exc()
            return Response({'detail': 'Server error in Login'}, status=500)


# 🟢 Logout
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail': 'Logged out successfully'}, status=200)
        except:
            return Response({'detail': 'Server error in Logout'}, status=500)


# 🟢 User Profile
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            return Response(UserSerializer(request.user).data, status=200)
        except:
            traceback.print_exc()
            return Response({'detail': 'Error fetching profile'}, status=500)

    def put(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        except:
            traceback.print_exc()
            return Response({'detail': 'Error updating profile'}, status=500)


# 🟢 Notification Settings
class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            serializer = NotificationSettingsSerializer(request.user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

            return Response(serializer.errors, status=400)
        except:
            traceback.print_exc()
            return Response({'detail': 'Error updating notifications'}, status=500)


# 🟢 Delivery Address
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


# 🟢 Delete Account
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            DeliveryAddress.objects.filter(user=user).delete()

            try:
                user.auth_token.delete()
            except:
                pass

            user.delete()
            return Response({"detail": "Account deleted successfully"}, status=200)

        except:
            traceback.print_exc()
            return Response({'detail': 'Error deleting account'}, status=500)


# 🟢 Forgot Password
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
                message=f"Use this token to reset password: {token}",
                from_email="noreply@maakaswad.com",
                recipient_list=[email],
            )

            return Response({'detail': 'Reset token sent'}, status=200)

        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)


# 🟢 Reset Password
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
