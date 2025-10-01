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
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("delivery_address")
            .prefetch_related("items__food_item")
            .order_by("-created_at")
        )


# ✅ Get details of a specific order
class UserOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("delivery_address")
            .prefetch_related("items__food_item")
        )


# ✅ Cancel an order within 2 minutes
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            if order.status.lower() != "pending":
                return Response(
                    {"detail": "Order cannot be cancelled (already processed)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if now() - order.created_at > timedelta(minutes=2):
                return Response(
                    {"detail": "Cancel period expired. You cannot cancel this order."},
                    status=status.HTTP_400_BAD_REQUEST
                )

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


# ✅ List all delivery addresses
class ListDeliveryAddressesView(generics.ListAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user).order_by('-id')


# ✅ Retrieve / Update / Delete delivery address
class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


# ✅ Track a live order
class TrackOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = (
                Order.objects
                .select_related("delivery_address")
                .filter(id=order_id, user=request.user)
                .first()
            )

            if not order:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            delivery_address = order.delivery_address
            restaurant = getattr(order, "restaurant", None)

            data = {
                "id": order.id,
                "status": order.status,
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "driver_location": {
                    "latitude": float(getattr(order, "driver_latitude", 0.0)) if order.driver_latitude else None,
                    "longitude": float(getattr(order, "driver_longitude", 0.0)) if order.driver_longitude else None,
                },
                "destination": {
                    "latitude": float(delivery_address.latitude) if delivery_address and delivery_address.latitude else None,
                    "longitude": float(delivery_address.longitude) if delivery_address and delivery_address.longitude else None,
                },
                "restaurant_location": {
                    "latitude": float(getattr(restaurant, "latitude", 0.0)) if restaurant else None,
                    "longitude": float(getattr(restaurant, "longitude", 0.0)) if restaurant else None,
                },
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": f"Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
