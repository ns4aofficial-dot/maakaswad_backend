from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from food.models import FoodItem

# ✅ List the user's cart and its items
class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ✅ Add a CartItem to the Cart (POST)
class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # If item already in cart, update quantity
        food_item = serializer.validated_data['food_item']
        quantity = serializer.validated_data.get('quantity', 1)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            food_item=food_item,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()


# ✅ Delete a CartItem from cart
class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'  # pk of CartItem

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)
