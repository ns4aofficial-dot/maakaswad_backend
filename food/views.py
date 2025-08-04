from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from .models import Category, FoodItem, Order, OrderItem, Favorite, SupportTicket
from .serializers import (
    CategorySerializer,
    FoodItemSerializer,
    OrderSerializer,
    FavoriteSerializer,
    SupportTicketSerializer,
)


# ✅ Category List
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# ✅ Food Items List
class FoodItemListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return FoodItem.objects.filter(category__id=category_id, is_available=True)
        return FoodItem.objects.filter(is_available=True)


# ✅ Delete Food Item
class FoodItemDeleteView(generics.DestroyAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAdminUser]


# ✅ My Orders
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# ✅ Place Order
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        order = Order.objects.create(user=request.user, total_price=0, status='pending')

        for item in items:
            try:
                food = FoodItem.objects.get(id=item['food_item'])
            except FoodItem.DoesNotExist:
                return Response({'error': f"Food item {item['food_item']} not found"},
                                status=status.HTTP_400_BAD_REQUEST)

            quantity = int(item['quantity'])
            price = food.price * quantity
            total_price += price

            OrderItem.objects.create(order=order, food_item=food, quantity=quantity, price=price)

        order.total_price = total_price
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ✅ Cancel Order
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status.lower() != 'pending':
            return Response({'error': 'Only pending orders can be cancelled'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()
        return Response({'success': 'Order cancelled successfully'}, status=status.HTTP_200_OK)


# ✅ Favorite List
class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)


# ✅ Toggle Favorite (Add/Remove)
class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, food_id):
        try:
            food_item = FoodItem.objects.get(id=food_id)
        except FoodItem.DoesNotExist:
            return Response({'error': 'Food item not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, food_item=food_item)
        if not created:
            favorite.delete()
            return Response({'removed': f'{food_item.name} removed from favorites'})
        return Response({'added': f'{food_item.name} added to favorites'})


# ✅ Support Ticket List & Create
class SupportTicketListCreateView(generics.ListCreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users see their own tickets
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
