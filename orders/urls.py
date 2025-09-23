from django.urls import path
from .views import (
    PlaceOrderView,
    UserOrderListView,
    UserOrderDetailView,
    CancelOrderView,
    CreateDeliveryAddressView,
    ListDeliveryAddressesView,
    DeliveryAddressDetailView,
    TrackOrderView,
)

urlpatterns = [
    # 📦 Order Endpoints
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),
    path('my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='order-detail'),
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),

    # 🚚 Delivery Address Endpoints
    path('address/create/', CreateDeliveryAddressView.as_view(), name='create-address'),
    path('address/', ListDeliveryAddressesView.as_view(), name='list-addresses'),
    path('address/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),

    # 🛰️ Live Order Tracking
    # ✅ This matches Flutter's GET /api/orders/track/<order_id>/
    path('track/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),
]
