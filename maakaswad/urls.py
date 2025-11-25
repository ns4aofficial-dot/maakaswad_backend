from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve

def health_check(request):
    return JsonResponse({"status": "ok", "message": "Maakaswad backend running!"})

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', health_check),

    # USERS (includes Social Login)
    path('api/users/', include('users.urls')),

    # Food
    path('api/food/', include('food.urls')),

    # Cart
    path('api/cart/', include('cart.urls')),

    # Orders
    path('api/orders/', include('orders.urls')),

    # Payments
    path('api/payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
