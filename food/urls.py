from django.urls import path
from .views import (
    CategoryListView,
    FoodItemListView,
    FoodItemDeleteView,
    MyOrdersView,
    PlaceOrderView,
    CancelOrderView,
    FavoriteListView,
    ToggleFavoriteView,
    SupportTicketListCreateView,   # ✅ New
)

urlpatterns = [
    # ✅ Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # ✅ Food Items
    path('items/', FoodItemListView.as_view(), name='fooditem-list'),
    path('items/<int:pk>/delete/', FoodItemDeleteView.as_view(), name='fooditem-delete'),

    # ✅ Orders
    path('order/my-orders/', MyOrdersView.as_view(), name='my-orders'),
    path('order/place/', PlaceOrderView.as_view(), name='place-order'),
    path('order/cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),

    # ✅ Favorites
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/toggle/<int:food_id>/', ToggleFavoriteView.as_view(), name='toggle-favorite'),

    # ✅ Support Tickets
    path('support/', SupportTicketListCreateView.as_view(), name='support-ticket'),
]
