from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DeliveryAddressSerializer,
    NotificationSettingsSerializer
)
from .models import DeliveryAddress
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
import traceback

User = get_user_model()

# 🩺 Health Check View
@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "ok"})

# ✅ Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("❌ Error in RegisterView:", str(e))
            traceback.print_exc()
            return Response({'detail': 'Server error in Register'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Login View (Optimized with Q lookup)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            identifier = request.data.get('identifier')
            password = request.data.get('password')

            if not identifier or not password:
                return Response(
                    {'detail': 'Please provide identifier and password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(
                Q(email__iexact=identifier) |
                Q(phone=identifier) |
                Q(username__iexact=identifier)
            ).first()

            if not user:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if not user.check_password(password):
                return Response({'detail': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'notifications_enabled': getattr(user, 'notifications_enabled', False),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ Error in LoginView:", str(e))
            traceback.print_exc()
            return Response(
                {'detail': 'Server error in Login'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ✅ Logout View
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("❌ Error in LogoutView:", str(e))
            traceback.print_exc()
            return Response({'detail': 'Server error in Logout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ User Profile View
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        except Exception as e:
            print("❌ Error in UserProfileView GET:", str(e))
            traceback.print_exc()
            return Response({'detail': 'Server error fetching profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("❌ Error in UserProfileView PUT:", str(e))
            traceback.print_exc()
            return Response({'detail': 'Server error updating profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Notification Settings View
class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'notifications_enabled': request.user.notifications_enabled}, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            serializer = NotificationSettingsSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("❌ Error in NotificationSettingsView:", str(e))
            traceback.print_exc()
            return Response({'detail': 'Server error updating notifications'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Delivery Address Views
class DeliveryAddressListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            print("❌ Error in DeliveryAddressListCreateView:", str(e))
            traceback.print_exc()
            raise

class DeliveryAddressDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeliveryAddressSerializer

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

# ✅ Forgot Password View
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'detail': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            reset_token = get_random_string(32)
            user.reset_token = reset_token
            user.save(update_fields=[])

            send_mail(
                subject="Password Reset Request",
                message=f"Use this token to reset your password: {reset_token}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({'detail': 'Password reset token sent to email'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'detail': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

# ✅ Reset Password View
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([email, token, new_password]):
            return Response({'detail': 'Email, token, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if getattr(user, "reset_token", None) != token:
                return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.reset_token = None
            user.save()

            return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
