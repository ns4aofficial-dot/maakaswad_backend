import logging
from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, DeliveryAddress
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    PlaceOrderSerializer,
    DeliveryAddressSerializer,
    DriverLocationUpdateSerializer,
    ChefStatusUpdateSerializer,
    CaptainStatusUpdateSerializer,
)

logger = logging.getLogger(__name__)


# ==========================================================
# 🛒 CUSTOMER - Place Order
# ==========================================================
class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PlaceOrderSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderDetailSerializer(order).data, status=201)

        return Response(serializer.errors, status=400)


# ==========================================================
# 🛒 CUSTOMER - My Orders
# ==========================================================
class UserOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class UserOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ==========================================================
# ❌ CUSTOMER - Cancel Order
# ==========================================================
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pending":
            return Response({"detail": "Order cannot be cancelled."}, status=400)

        if now() - order.created_at > timedelta(minutes=2):
            return Response({"detail": "Cancel period expired."}, status=400)

        order.status = "cancelled"
        order.save(update_fields=["status"])

        return Response({"detail": "Order cancelled successfully."})


# ==========================================================
# 👩‍🍳 CHEF - View Orders
# ==========================================================
class ChefOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role != "chef":
            return Order.objects.none()

        return Order.objects.filter(
            Q(assigned_chef=self.request.user) |
            Q(status="pending")
        ).distinct().order_by("-created_at")


# ==========================================================
# 👩‍🍳 CHEF - Accept Order
# ==========================================================
class ChefAcceptOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):

        if request.user.role != "chef":
            return Response({"detail": "Only chef allowed."}, status=403)

        order = get_object_or_404(Order, id=order_id)

        if order.status != "pending":
            return Response({"detail": "Order already taken."}, status=400)

        order.assigned_chef = request.user
        order.status = "accepted"
        order.save(update_fields=["assigned_chef", "status"])

        return Response({"detail": "Order accepted successfully."})


# ==========================================================
# 👩‍🍳 CHEF - Update Status
# ==========================================================
class ChefUpdateStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, order_id):

        if request.user.role != "chef":
            return Response({"detail": "Only chef allowed."}, status=403)

        order = get_object_or_404(
            Order,
            id=order_id,
            assigned_chef=request.user
        )

        serializer = ChefStatusUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Order status updated by chef."})

        return Response(serializer.errors, status=400)


# ==========================================================
# 🚴 CAPTAIN - View Orders
# ==========================================================
class CaptainOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role != "captain":
            return Order.objects.none()

        return Order.objects.filter(
            assigned_captain=self.request.user
        ).order_by("-created_at")


# ==========================================================
# 🚴 CAPTAIN - Update Status
# ==========================================================
class CaptainUpdateStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, order_id):

        if request.user.role != "captain":
            return Response({"detail": "Only captain allowed."}, status=403)

        order = get_object_or_404(
            Order,
            id=order_id,
            assigned_captain=request.user
        )

        serializer = CaptainStatusUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Order status updated by captain."})

        return Response(serializer.errors, status=400)

# ==========================================================
# 🚴 Assign Captain (AUTO ASSIGN 🔥)
# ==========================================================
class AssignCaptainView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):

        # Only chef can assign
        if request.user.role != "chef":
            return Response({"detail": "Only chef allowed."}, status=403)

        # Get order
        order = get_object_or_404(Order, id=order_id)

        from users.models import User

        # 🔥 AUTO SELECT FIRST AVAILABLE CAPTAIN
        captain = User.objects.filter(role="captain").first()

        if not captain:
            return Response(
                {"detail": "No captain available"},
                status=404
            )

        # Assign captain
        order.assigned_captain = captain
        order.status = "assigned"
        order.save(update_fields=["assigned_captain", "status"])

        return Response({
            "detail": "Captain assigned automatically",
            "captain": captain.username
        })

# ==========================================================
# 🚚 Track Order (Customer)
# ==========================================================
class TrackOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        return Response(OrderSerializer(order).data)


# ==========================================================
# 📍 Update Driver Location
# ==========================================================
class UpdateDriverLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, order_id):

        if request.user.role != "captain":
            return Response({"detail": "Only captain allowed."}, status=403)

        order = get_object_or_404(
            Order,
            id=order_id,
            assigned_captain=request.user
        )

        serializer = DriverLocationUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Driver location updated."})

        return Response(serializer.errors, status=400)


# ==========================================================
# 🏠 Delivery Address
# ==========================================================
class CreateDeliveryAddressView(generics.CreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListDeliveryAddressesView(generics.ListAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


# ==========================================================
# 💰 CHEF EARNINGS
# ==========================================================
class ChefEarningsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        if request.user.role != "chef":
            return Response({"detail": "Only chef allowed."}, status=403)

        delivered_orders = Order.objects.filter(
            assigned_chef=request.user,
            status="delivered"
        )

        total_earnings = delivered_orders.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        today_earnings = delivered_orders.filter(
            created_at__date=now().date()
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        week_earnings = delivered_orders.filter(
            created_at__gte=now() - timedelta(days=7)
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        orders_completed = delivered_orders.count()

        return Response({
            "today": today_earnings,
            "week": week_earnings,
            "total": total_earnings,
            "orders": orders_completed
        })

    # ==========================================================
# 🚴 CAPTAIN EARNINGS
# ==========================================================
class CaptainEarningsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        if request.user.role != "captain":
            return Response({"detail": "Only captain allowed."}, status=403)

        delivered_orders = Order.objects.filter(
            assigned_captain=request.user,
            status="delivered"   # ⚠️ must match your DB value
        )

        total_earnings = delivered_orders.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        today_earnings = delivered_orders.filter(
            created_at__date=now().date()
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        week_earnings = delivered_orders.filter(
            created_at__gte=now() - timedelta(days=7)
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        orders_completed = delivered_orders.count()

        return Response({
            "today": today_earnings,
            "week": week_earnings,
            "total": total_earnings,
            "orders": orders_completed
        })