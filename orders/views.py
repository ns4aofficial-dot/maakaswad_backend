from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, DeliveryAddress
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    DeliveryAddressSerializer,
)


# -----------------------------
# 🛒 PLACE ORDER
# -----------------------------
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            return Response({"message": "Order placed successfully", "order_id": order.id}, status=201)
        return Response(serializer.errors, status=400)


# -----------------------------
# 📦 LIST USER ORDERS
# -----------------------------
class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data)


# -----------------------------
# 📄 ORDER DETAIL VIEW
# -----------------------------
class UserOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


# -----------------------------
# ❌ CANCEL ORDER
# -----------------------------
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status not in ["Pending", "Accepted"]:
            return Response({"error": "Order cannot be cancelled"}, status=400)

        order.status = "Cancelled"
        order.save()
        return Response({"message": "Order cancelled"})


# -----------------------------
# 🏠 CREATE DELIVERY ADDRESS
# -----------------------------
class CreateDeliveryAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeliveryAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# -----------------------------
# 📍 LIST ADDRESSES
# -----------------------------
class ListDeliveryAddressesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = DeliveryAddress.objects.filter(user=request.user)
        serializer = DeliveryAddressSerializer(addresses, many=True)
        return Response(serializer.data)


# -----------------------------
# 🏠 ADDRESS DETAIL
# -----------------------------
class DeliveryAddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        address = get_object_or_404(DeliveryAddress, id=pk, user=request.user)
        serializer = DeliveryAddressSerializer(address)
        return Response(serializer.data)


# -----------------------------
# 🚚 TRACK ORDER
# -----------------------------
class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return Response({
            "order_id": order.id,
            "status": order.status,
            "driver_latitude": order.driver_latitude,
            "driver_longitude": order.driver_longitude,
        })


# -----------------------------
# 📍 UPDATE DRIVER LOCATION
# -----------------------------
class UpdateDriverLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        order.driver_latitude = request.data.get("latitude")
        order.driver_longitude = request.data.get("longitude")
        order.save()

        return Response({"message": "Driver location updated"})


# -----------------------------
# ✅ ACCEPT ORDER
# -----------------------------
class AcceptOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.status = "Accepted"
        order.save()
        return Response({"message": "Order accepted"})


# -----------------------------
# ❌ REJECT ORDER
# -----------------------------
class RejectOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.status = "Rejected"
        order.save()
        return Response({"message": "Order rejected"})
