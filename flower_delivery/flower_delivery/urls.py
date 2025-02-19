from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.views import get_user_by_telegram_id, UserViewSet
from orders.views import OrderViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'orders', OrderViewSet, basename="orders")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("orders/", include(("orders.urls", "orders"))),
    path("users/", include("users.urls")),
    path("bot/", include("telegram_bot.urls")),

    # ✅ API
    path("api/", include(router.urls)),
    path("api/get_user/", get_user_by_telegram_id, name="get-user"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
