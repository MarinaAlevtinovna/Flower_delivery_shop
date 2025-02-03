from django.urls import path
from .views import cart_view, add_to_cart, remove_from_cart

app_name = "orders"

urlpatterns = [
    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", remove_from_cart, name="remove_from_cart"),
]
