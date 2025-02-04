from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ProductViewSet
from .views import get_user

router = DefaultRouter()
router.register(r'orders', OrderViewSet)  # Заказы
router.register(r'products', ProductViewSet)  # Товары

urlpatterns = [
    path('', include(router.urls)),
    path("get_user/", get_user, name="get_user")
]

