from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from orders.models import Order
from catalog.models import Product

class OrderAPITests(TestCase):
    """Тестируем API заказов"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(self.user)

        self.product = Product.objects.create(name="Роза", price=1500.00)
        self.order = Order.objects.create(user=self.user)
        self.order.products.add(self.product)

    def test_get_orders(self):
        """Проверяем, что API возвращает заказы пользователя"""
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_order(self):
        """Проверяем создание заказа через API"""
        data = {"user": self.user.id, "products": [self.product.id]}
        response = self.client.post(reverse("order-list"), data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
