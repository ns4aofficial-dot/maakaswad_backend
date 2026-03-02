from django.urls import path
from .views import (
    CategoryListView,
    FoodItemListView,
    FoodItemDetailView,

    # 🔵 NEW CHEF VIEWS
    ChefFoodItemListCreateView,
    ChefFoodItemDetailView,
    ChefFoodItemDeleteView,

    FavoriteListView,
    ToggleFavoriteView,
    SupportTicketListCreateView,
)

urlpatterns = [

    # ======================================================
    # 🟢 CATEGORY
    # ======================================================
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # ======================================================
    # 🟢 CUSTOMER FOOD APIs
    # ======================================================
    path('items/', FoodItemListView.as_view(), name='fooditem-list'),
    path('items/<int:pk>/', FoodItemDetailView.as_view(), name='fooditem-detail'),

    # ======================================================
    # 🔵 CHEF MENU APIs
    # ======================================================
    path('chef/items/', ChefFoodItemListCreateView.as_view(), name='chef-food-list-create'),
    path('chef/items/<int:pk>/', ChefFoodItemDetailView.as_view(), name='chef-food-detail-update'),
    path('chef/items/<int:pk>/delete/', ChefFoodItemDeleteView.as_view(), name='chef-food-delete'),

    # ======================================================
    # ⭐ FAVORITES
    # ======================================================
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/toggle/<int:food_id>/', ToggleFavoriteView.as_view(), name='toggle-favorite'),

    # ======================================================
    # 🎟 SUPPORT
    # ======================================================
    path('support/', SupportTicketListCreateView.as_view(), name='support-ticket'),
]