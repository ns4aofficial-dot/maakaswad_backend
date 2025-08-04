from datetime import timedelta
from django.utils.timezone import now
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, DeliveryAddress
from .serializers import (
    OrderSerializer,
    PlaceOrderSerializer,
    DeliveryAddressSerializer,
)


# ✅ Place a new order
class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ List all orders for the logged-in user
class UserOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# ✅ Get details of a specific order (owned by user)
class UserOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ✅ Cancel an order within 2 minutes of placing
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            if order.status.lower() != "pending":
                return Response(
                    {"detail": "❌ Order cannot be cancelled (already processed)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if now() - order.created_at > timedelta(minutes=2):
                return Response(
                    {"detail": "⏰ Cancel period expired. You cannot cancel this order."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.status = "Cancelled"
            order.save()
            return Response({"detail": "✅ Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"detail": "❌ Order not found."}, status=status.HTTP_404_NOT_FOUND)


# ✅ Create a new delivery address
class CreateDeliveryAddressView(generics.CreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ✅ List all delivery addresses for the logged-in user
class ListDeliveryAddressesView(generics.ListAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user).order_by('-id')


# ✅ Update/Delete delivery address
class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


# 🛰️ Live Order Tracking
class TrackOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.select_related("delivery_address").get(id=order_id, user=request.user)

            delivery_address = getattr(order, "delivery_address", None)
            restaurant = getattr(order, "restaurant", None)  # Optional, if added later

            data = {
                "id": order.id,
                "status": order.status,
                "total_price": str(order.total_amount),  # ✅ fixed field name
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),

                # Driver location
                "driver_location": {
                    "latitude": order.driver_latitude or 17.3850,
                    "longitude": order.driver_longitude or 78.4867,
                },

                # Destination (user delivery address, fallback values if None)
                "destination": {
                    "latitude": getattr(delivery_address, "latitude", 17.4000),
                    "longitude": getattr(delivery_address, "longitude", 78.4800),
                },

                # Restaurant location (dummy if None)
                "restaurant_latitude": getattr(restaurant, "latitude", 17.3850),
                "restaurant_longitude": getattr(restaurant, "longitude", 78.4867),
            }

            return Response(data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"detail": "❌ Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"⚠️ Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
