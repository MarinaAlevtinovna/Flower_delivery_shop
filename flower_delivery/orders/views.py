from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Product
from django.contrib import messages
from .forms import OrderForm
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

User = get_user_model()

@api_view(["GET"])
@permission_classes([AllowAny])  # Разрешаем доступ без токена
def get_user(request):
    telegram_id = request.GET.get("telegram_id")

    if not telegram_id:
        return Response({"error": "Telegram ID is required"}, status=400)

    # Создаём пользователя, если его нет, указывая уникальный email
    user, created = User.objects.get_or_create(
        username=f"user_{telegram_id}",
        defaults={
            "password": "securepass123",
            "email": f"user_{telegram_id}@example.com"  # Уникальный email
        }
    )

    return Response({"id": user.id, "username": user.username})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        telegram_id = request.GET.get("user")  # Получаем Telegram ID

        if telegram_id:
            user = User.objects.filter(username=f"user_{telegram_id}").first()
            if user:
                self.queryset = self.queryset.filter(user=user)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        telegram_id = self.request.data.get("user")  # Берём Telegram ID из запроса

        # Проверяем, есть ли пользователь с таким Telegram ID, и создаём его при необходимости
        user, created = User.objects.get_or_create(
            username=f"user_{telegram_id}",
            defaults={
                "password": "securepass123",
                "email": f"user_{telegram_id}@example.com"  # Генерируем уникальный email
            }
        )

        # Сохраняем заказ с этим пользователем
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

