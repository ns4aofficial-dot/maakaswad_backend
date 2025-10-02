from django.urls import path
from .views import (
    CartListCreateView,
    AddToCartView,
    CartItemDeleteView,
    CartItemUpdateView,  # ✅ New import
)

urlpatterns = [
    path('', CartListCreateView.as_view(), name='cart-list-create'),             # GET/POST - View Cart
    path('add/', AddToCartView.as_view(), name='cart-add'),                      # POST - Add item to cart
    path('item/delete/<int:pk>/', CartItemDeleteView.as_view(), name='cart-item-delete'),  # DELETE - Remove item
    path('item/update/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),  # PUT - Update item quantity
]
