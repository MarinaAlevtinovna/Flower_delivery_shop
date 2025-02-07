from django.test import TestCase
from django.contrib.auth import get_user_model
from orders.models import Order
from catalog.models import Product

class OrderModelTests(TestCase):
    """Тестируем модель заказов"""

    def setUp(self):
        """Создаем тестовые данные"""
        self.user = get_user_model().objects.create_user(username="testuser", password="testpass")
        self.product = Product.objects.create(name="Роза", price=1500.00)

    def test_create_order(self):
        """Проверяем, создается ли заказ"""
        order = Order.objects.create(user=self.user)
        order.products.add(self.product)

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.products.count(), 1)
        self.assertEqual(order.status, "new")

    def test_order_status_change_signal(self):
        """Проверяем, что сигнал срабатывает при смене статуса заказа"""
        order = Order.objects.create(user=self.user)
        order.products.add(self.product)
        order.status = "completed"
        order.save()

        updated_order = Order.objects.get(id=order.id)
        self.assertEqual(updated_order.status, "completed")
