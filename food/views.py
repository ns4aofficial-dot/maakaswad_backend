from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from .models import Category, FoodItem, Favorite, SupportTicket
from .serializers import (
    CategorySerializer,
    FoodItemSerializer,
    FavoriteSerializer,
    SupportTicketSerializer,
)

# Category List
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# Food Items List
class FoodItemListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return FoodItem.objects.filter(category__id=category_id, is_available=True)
        return FoodItem.objects.filter(is_available=True)

# Food Item Detail
class FoodItemDetailView(generics.RetrieveAPIView):
    queryset = FoodItem.objects.filter(is_available=True)
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]

# Delete Food Item
class FoodItemDeleteView(generics.DestroyAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAdminUser]

# Favorite List
class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

# Toggle Favorite
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

# Support Ticket
class SupportTicketListCreateView(generics.ListCreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
