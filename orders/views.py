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


# ✅ List all orders for the logged-in user (fast queryset)
class UserOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Use select_related/prefetch_related to reduce DB queries
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("delivery_address")
            .prefetch_related("items__food_item")
            .order_by("-created_at")
        )


# ✅ Get details of a specific order (owned by user)
class UserOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("delivery_address").prefetch_related("items__food_item")


# ✅ Cancel an order within 2 minutes of placing
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # Only pending orders can be cancelled
            if order.status.lower() != "pending":
                return Response(
                    {"detail": "Order cannot be cancelled (already processed)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check cancel window (2 minutes)
            elapsed = now() - order.created_at
            if elapsed > timedelta(minutes=2):
                return Response(
                    {"detail": "Cancel period expired. You cannot cancel this order."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use the lowercase status value that matches model choices
            order.status = "cancelled"
            order.save(update_fields=["status"])
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            # Fetch order with delivery_address (faster)
            order = Order.objects.select_related("delivery_address").filter(id=order_id, user=request.user).first()
            if not order:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            delivery_address = order.delivery_address
            # restaurant may not exist on Order model yet — guard it
            restaurant = getattr(order, "restaurant", None)

            data = {
                "id": order.id,
                "status": order.status,
                "total_price": str(order.total_amount),
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),

                # Driver location (fallback to None or sensible default)
                "driver_location": {
                    "latitude": float(order.driver_latitude) if order.driver_latitude is not None else None,
                    "longitude": float(order.driver_longitude) if order.driver_longitude is not None else None,
                },

                # Destination (user delivery address, fallback to None)
                "destination": {
                    "latitude": float(getattr(delivery_address, "latitude", None)) if delivery_address else None,
                    "longitude": float(getattr(delivery_address, "longitude", None)) if delivery_address else None,
                },

                # Restaurant location (if available)
                "restaurant_location": {
                    "latitude": float(getattr(restaurant, "latitude", None)) if restaurant else None,
                    "longitude": float(getattr(restaurant, "longitude", None)) if restaurant else None,
                },
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": f"Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
