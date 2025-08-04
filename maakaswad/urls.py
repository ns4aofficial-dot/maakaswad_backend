from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# ✅ Optional: Health check view
def health_check(request):
    return JsonResponse({"status": "ok", "message": "Maakaswad backend running!"})

urlpatterns = [
    # 🛠️ Django Admin
    path('admin/', admin.site.urls),

    # 🔍 API Health Check
    path('', health_check, name='health-check'),

    # 👤 User APIs - Auth, Profile, Address
    path('api/users/', include('users.urls')),       # register, login (email/phone/username), logout, profile, addresses

    # 🍽️ Food APIs - Categories & Items
    path('api/food/', include('food.urls')),         # category list, item list/details

    # 🛒 Cart APIs
    path('api/cart/', include('cart.urls')),         # cart add/view/delete

    # 📦 Order APIs
    path('api/orders/', include('orders.urls')),     # order place/view/history

    # 💳 Payment APIs - Razorpay
    path('api/payments/', include('payments.urls')), # initiate/verify Razorpay payment
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Serve static files (CSS/JS) in development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
