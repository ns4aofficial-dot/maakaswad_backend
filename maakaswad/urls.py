from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve

# ✅ Health Check View
def health_check(request):
    return JsonResponse({"status": "ok", "message": "Maakaswad backend running!"})

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Health Check
    path('', health_check, name='health-check'),

    # 👤 User APIs
    path('api/users/', include('users.urls')),

    # 🍽️ Food APIs
    path('api/food/', include('food.urls')),

    # 🛒 Cart APIs
    path('api/cart/', include('cart.urls')),

    # 📦 Order APIs
    path('api/orders/', include('orders.urls')),

    # 💳 Payment APIs
    path('api/payments/', include('payments.urls')),
]

# ✅ Serve media during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Fallback for production with Whitenoise
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
