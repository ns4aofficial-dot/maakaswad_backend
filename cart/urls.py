from django.urls import path
from .views import (
    CartListCreateView,
    AddToCartView,
    CartItemDeleteView,
)

urlpatterns = [
    path('', CartListCreateView.as_view(), name='cart-list-create'),             # GET/POST - View Cart
    path('add/', AddToCartView.as_view(), name='cart-add'),                      # POST - Add item to cart
    path('item/delete/<int:pk>/', CartItemDeleteView.as_view(), name='cart-item-delete'),  # DELETE - Remove item
]
