from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("orders/", include("orders.urls")),
    path("api/", include("orders.api_urls")),
    path("bot/", include("telegram_bot.urls")),
]

