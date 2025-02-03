from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Product

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

