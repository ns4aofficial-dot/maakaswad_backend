from django.urls import path
from .views import (
    PlaceOrderView,
    UserOrderListView,
    UserOrderDetailView,
    CancelOrderView,
    CreateDeliveryAddressView,
    ListDeliveryAddressesView,
    DeliveryAddressDetailView,
)

urlpatterns = [
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),
    path('my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='order-detail'),
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),

    path('address/create/', CreateDeliveryAddressView.as_view(), name='create-address'),
    path('address/', ListDeliveryAddressesView.as_view(), name='list-addresses'),
    path('address/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),
]
