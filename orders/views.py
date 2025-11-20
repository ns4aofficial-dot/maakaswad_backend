from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Order
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
)
from users.models import DeliveryAddress
from users.serializers import DeliveryAddressSerializer


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response({"message": "Order placed successfully", "order_id": order.id}, status=201)
        return Response(serializer.errors, status=400)


class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data)


class UserOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status not in ["Placed", "Accepted"]:
            return Response({"error": "Order cannot be cancelled"}, status=400)

        order.status = "Cancelled"
        order.save()
        return Response({"message": "Order cancelled"})


class CreateDeliveryAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeliveryAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ListDeliveryAddressesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = DeliveryAddress.objects.filter(user=request.user)
        serializer = DeliveryAddressSerializer(addresses, many=True)
        return Response(serializer.data)


class DeliveryAddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        address = get_object_or_404(DeliveryAddress, id=pk, user=request.user)
        serializer = DeliveryAddressSerializer(address)
        return Response(serializer.data)
