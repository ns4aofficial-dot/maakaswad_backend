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


# ==========================================================
# 🟢 CATEGORY LIST (PUBLIC)
# ==========================================================
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# ==========================================================
# 🟢 CUSTOMER FOOD LIST (PUBLIC)
# ==========================================================
class FoodItemListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')

        queryset = FoodItem.objects.filter(is_available=True)

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset


# ==========================================================
# 🟢 CUSTOMER FOOD DETAIL
# ==========================================================
class FoodItemDetailView(generics.RetrieveAPIView):
    queryset = FoodItem.objects.filter(is_available=True)
    serializer_class = FoodItemSerializer
    permission_classes = [AllowAny]


# ==========================================================
# 🔵 CHEF - VIEW OWN MENU
# ==========================================================
class ChefFoodItemListCreateView(generics.ListCreateAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "chef":
            return FoodItem.objects.none()

        return FoodItem.objects.filter(chef=self.request.user)

    def perform_create(self, serializer):
        serializer.save(chef=self.request.user)


# ==========================================================
# 🔵 CHEF - UPDATE OWN ITEM
# ==========================================================
class ChefFoodItemDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "chef":
            return FoodItem.objects.none()

        return FoodItem.objects.filter(chef=self.request.user)


# ==========================================================
# 🔵 CHEF - DELETE OWN ITEM
# ==========================================================
class ChefFoodItemDeleteView(generics.DestroyAPIView):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "chef":
            return FoodItem.objects.none()

        return FoodItem.objects.filter(chef=self.request.user)


# ==========================================================
# ⭐ FAVORITES
# ==========================================================
class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)


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


# ==========================================================
# 🎟 SUPPORT TICKET
# ==========================================================
class SupportTicketListCreateView(generics.ListCreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)