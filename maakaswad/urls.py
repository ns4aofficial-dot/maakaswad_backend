from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from django.views.static import serve
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


# ✅ Health check class-based view
@method_decorator(csrf_exempt, name="dispatch")
class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok", "message": "Maakaswad backend running!"})

    def head(self, request, *args, **kwargs):
        return HttpResponse(status=200)


urlpatterns = [
    # 🛠️ Django Admin
    path("admin/", admin.site.urls),

    # 🔍 API Health Check
    path("", HealthCheckView.as_view(), name="health-check"),

    # 👤 User APIs - Auth, Profile, Address
    path("api/users/", include("users.urls")),       

    # 🍽️ Food APIs - Categories & Items
    path("api/food/", include("food.urls")),         

    # 🛒 Cart APIs
    path("api/cart/", include("cart.urls")),         

    # 📦 Order APIs
    path("api/orders/", include("orders.urls")),     

    # 💳 Payment APIs - Razorpay
    path("api/payments/", include("payments.urls")), 
]


# ✅ Media files (dev only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Static files (dev & prod)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Whitenoise fallback for static in production
if not settings.DEBUG:
    urlpatterns += [
        re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    ]
