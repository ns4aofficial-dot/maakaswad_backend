from django.urls import path
from .views import (

    # Customer
    PlaceOrderView,
    UserOrderListView,
    UserOrderDetailView,
    CancelOrderView,

    # Delivery Address
    CreateDeliveryAddressView,
    ListDeliveryAddressesView,
    DeliveryAddressDetailView,

    # Tracking
    TrackOrderView,
    UpdateDriverLocationView,

    # Chef
    ChefOrderListView,
    ChefAcceptOrderView,
    ChefUpdateStatusView,
    ChefEarningsView,   # ✅ NEW IMPORT

    # Captain
    CaptainOrderListView,
    CaptainUpdateStatusView,
    AssignCaptainView,
)

urlpatterns = [

    # ======================================================
    # 🛒 CUSTOMER ORDER APIs
    # ======================================================
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),
    path('my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='order-detail'),
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),

    # ======================================================
    # 🏠 DELIVERY ADDRESS APIs
    # ======================================================
    path('address/create/', CreateDeliveryAddressView.as_view(), name='create-address'),
    path('address/', ListDeliveryAddressesView.as_view(), name='list-addresses'),
    path('address/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),

    # ======================================================
    # 🚚 TRACKING APIs
    # ======================================================
    path('track/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),
    path('track/update-location/<int:order_id>/', UpdateDriverLocationView.as_view(), name='update-driver-location'),

    # ======================================================
    # 👩‍🍳 CHEF APIs
    # ======================================================
    path('chef/orders/', ChefOrderListView.as_view(), name='chef-orders'),
    path('chef/accept/<int:order_id>/', ChefAcceptOrderView.as_view(), name='chef-accept-order'),
    path('chef/update-status/<int:order_id>/', ChefUpdateStatusView.as_view(), name='chef-update-status'),

    # ⭐ CHEF EARNINGS
    path('chef/earnings/', ChefEarningsView.as_view(), name='chef-earnings'),

    # ======================================================
    # 🚴 CAPTAIN APIs
    # ======================================================
    path('captain/orders/', CaptainOrderListView.as_view(), name='captain-orders'),
    path('captain/update-status/<int:order_id>/', CaptainUpdateStatusView.as_view(), name='captain-update-status'),

    # Assign Captain
    path('assign-captain/<int:order_id>/', AssignCaptainView.as_view(), name='assign-captain'),
]