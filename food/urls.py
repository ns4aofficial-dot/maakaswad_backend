from django.urls import path
from .views import (
    CategoryListView,
    FoodItemListView,
    FoodItemDeleteView,
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

    # ✅ Favorites
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/toggle/<int:food_id>/', ToggleFavoriteView.as_view(), name='toggle-favorite'),

    # ✅ Support Tickets
    path('support/', SupportTicketListCreateView.as_view(), name='support-ticket'),
]
