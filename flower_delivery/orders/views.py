from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Product
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import OrderForm
from .models import Order
from users.models import CustomUser
from .serializers import OrderSerializer
from rest_framework import viewsets

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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

