from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import OrderForm
from catalog.models import Product
from users.models import CustomUser
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import ProductSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def get_product_or_404(product_id):
    """Функция для безопасного получения товара"""
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logging.warning(f"⚠️ Товар с ID {product_id} не найден!")
        return None


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_orders(request):
    """Возвращает заказы только текущего пользователя"""
    telegram_id = request.GET.get("telegram_id")

    if not telegram_id:
        return Response({"error": "Telegram ID is required"}, status=400)

    user = User.objects.filter(telegram_id=telegram_id).first()

    if not user:
        return Response({"message": "Пользователь не найден"}, status=404)

    orders = Order.objects.filter(user=user)  # 🔹 Фильтруем заказы по пользователю

    if not orders.exists():
        return Response({"message": "У вас пока нет заказов"}, status=200)

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтруем заказы только для текущего пользователя"""
        user = self.request.user
        return Order.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        telegram_id = request.GET.get("user")  # Получаем Telegram ID

        if telegram_id:
            user = User.objects.filter(username=f"user_{telegram_id}").first()
            if user:
                self.queryset = self.queryset.filter(user=user)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Привязывает заказ к пользователю"""
        telegram_id = self.request.data.get("telegram_id")

        if not telegram_id:
            raise serializers.ValidationError({"telegram_id": "Не указан Telegram ID"})

        user = User.objects.filter(telegram_id=telegram_id).first()

        if not user:
            raise serializers.ValidationError({"user": "Пользователь не найден!"})

        serializer.save(user=user)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []  # Открываем доступ


def cart_view(request):
    cart = request.session.get("cart", {})  # Получаем корзину из сессии
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items.append({"product": product, "quantity": quantity})
        total_price += product.price * quantity

    return render(request, "orders/cart.html", {"cart_items": cart_items, "total_price": total_price})

def add_to_cart(request, product_id):
    """Добавить товар в корзину по ID"""
    product = get_product_or_404(product_id)  # Получаем товар по ID

    if not product:
        messages.error(request, "Этот товар больше недоступен.")
        return redirect("orders:cart")

    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session["cart"] = cart  # Сохраняем изменения в сессии
    return redirect("orders:cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session["cart"] = cart
    return redirect("orders:cart")

def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Ваша корзина пуста!")
        return redirect("orders:cart")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            order = Order.objects.create(
                user=user,
                status="new"
            )
            products = Product.objects.filter(id__in=cart.keys())
            order.products.set(products)
            order.save()

            # Очистка корзины
            request.session["cart"] = {}

            messages.success(request, "Заказ успешно оформлен! Мы с вами свяжемся.")
            return redirect("home")
    else:
        form = OrderForm()

    return render(request, "orders/checkout.html", {"form": form})

