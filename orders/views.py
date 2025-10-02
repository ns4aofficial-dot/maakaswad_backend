import logging
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
    DriverLocationUpdateSerializer
)

logger = logging.getLogger(__name__)


# --- Place a new order ---
class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"PlaceOrderView called by user {request.user}")
        serializer = PlaceOrderSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                order = serializer.save()
                logger.info(f"Order #{order.id} placed successfully by user {request.user}")
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error placing order: {str(e)}")
                return Response({"detail": "Failed to place order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"PlaceOrderView validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- List all orders for the logged-in user ---
class UserOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        logger.info(f"UserOrderListView called by user {self.request.user}")
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("delivery_address")
            .prefetch_related("items__food_item")
            .order_by("-created_at")
        )


# --- Get details of a specific order ---
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


# --- Cancel an order within 2 minutes ---
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        logger.info(f"CancelOrderView called for order_id {order_id} by user {request.user}")
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if order.status.lower() != "pending":
                return Response({"detail": "Order cannot be cancelled (already processed)."}, status=status.HTTP_400_BAD_REQUEST)

            if now() - order.created_at > timedelta(minutes=2):
                return Response({"detail": "Cancel period expired."}, status=status.HTTP_400_BAD_REQUEST)

            order.status = "cancelled"
            order.save(update_fields=["status"])
            logger.info(f"Order #{order.id} cancelled successfully")
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            logger.warning(f"CancelOrderView: Order not found with ID {order_id}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"CancelOrderView error: {str(e)}")
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Create a new delivery address ---
class CreateDeliveryAddressView(generics.CreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        logger.info(f"CreateDeliveryAddressView called by user {self.request.user}")
        serializer.save(user=self.request.user)


# --- List all delivery addresses ---
class ListDeliveryAddressesView(generics.ListAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user).order_by('-id')


# --- Retrieve / Update / Delete delivery address ---
class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)


# --- Track a live order ---
class TrackOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        logger.info(f"TrackOrderView called for order_id {order_id} by user {request.user}")
        try:
            order = Order.objects.select_related("delivery_address").filter(id=order_id, user=request.user).first()
            if not order:
                logger.warning(f"TrackOrderView: Order not found with ID {order_id}")
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            delivery_address = order.delivery_address
            restaurant = getattr(order, "restaurant", None)

            data = {
                "id": order.id,
                "status": order.status,
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "driver_location": {
                    "latitude": float(order.driver_latitude) if order.driver_latitude else None,
                    "longitude": float(order.driver_longitude) if order.driver_longitude else None,
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
            logger.error(f"TrackOrderView error: {str(e)}")
            return Response({"detail": f"Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Update driver location ---
class UpdateDriverLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, order_id):
        logger.info(f"UpdateDriverLocationView called for order_id {order_id} by user {request.user}")
        try:
            order = Order.objects.get(id=order_id)
            serializer = DriverLocationUpdateSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Driver location updated for order #{order.id}")
                return Response({"detail": "Driver location updated successfully."}, status=status.HTTP_200_OK)

            logger.warning(f"UpdateDriverLocationView validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            logger.warning(f"UpdateDriverLocationView: Order not found with ID {order_id}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"UpdateDriverLocationView error: {str(e)}")
            return Response({"detail": f"Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Accept an order ---
class AcceptOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        logger.info(f"AcceptOrderView called for order_id {order_id} by user {request.user}")
        try:
            order = Order.objects.get(id=order_id)

            if order.status != "pending":
                return Response({"detail": "Order cannot be accepted."}, status=status.HTTP_400_BAD_REQUEST)

            order.status = "processing"
            order.accepted_by = request.user
            order.save(update_fields=["status", "accepted_by"])
            logger.info(f"Order #{order.id} accepted by {request.user}")
            return Response({"detail": "Order accepted successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            logger.warning(f"AcceptOrderView: Order not found with ID {order_id}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"AcceptOrderView error: {str(e)}")
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Reject an order ---
class RejectOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        logger.info(f"RejectOrderView called for order_id {order_id} by user {request.user}")
        try:
            order = Order.objects.get(id=order_id)

            if order.status != "pending":
                return Response({"detail": "Order cannot be rejected."}, status=status.HTTP_400_BAD_REQUEST)

            order.status = "cancelled"
            order.save(update_fields=["status"])
            logger.info(f"Order #{order.id} rejected by {request.user}")
            return Response({"detail": "Order rejected successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            logger.warning(f"RejectOrderView: Order not found with ID {order_id}")
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"RejectOrderView error: {str(e)}")
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
