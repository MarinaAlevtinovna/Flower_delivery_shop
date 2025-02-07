from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("orders/", include("orders.urls")),
    path("api/", include("orders.api_urls")),
    path("bot/", include("telegram_bot.urls")),
    path("api/", include("catalog.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)