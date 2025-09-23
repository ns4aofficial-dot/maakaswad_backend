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
    path('place/', PlaceOrderView.as_view(), name='place-order'),  # Place a new order
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),  # List all user's orders
    path('my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='order-detail'),  # Order details
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),  # Cancel order within 2 min

    # 🚚 Delivery Address Endpoints
    path('address/create/', CreateDeliveryAddressView.as_view(), name='create-address'),  # Add new address
    path('address/', ListDeliveryAddressesView.as_view(), name='list-addresses'),  # List addresses
    path('address/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),  # Update/Delete address

    # 🛰️ Live Order Tracking
    path('track/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),  # Track order location/status
]
