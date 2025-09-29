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
    path('place/', PlaceOrderView.as_view(), name='place-order'),                     # POST
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),              # GET
    path('my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='order-detail'),  # GET
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),   # POST / PATCH

    # 🚚 Delivery Address Endpoints
    path('address/create/', CreateDeliveryAddressView.as_view(), name='create-address'),  # POST
    path('address/', ListDeliveryAddressesView.as_view(), name='list-addresses'),         # GET
    path('address/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),# GET/PUT/DELETE

    # 🛰️ Live Order Tracking
    path('track/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),          # GET
]
