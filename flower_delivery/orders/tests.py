from django.test import TestCase
from users.models import CustomUser
from catalog.models import Product
from orders.models import Order

class OrderModelTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.user = CustomUser.objects.create(username="testuser", email="test@example.com", password="testpass")
        self.product = Product.objects.create(name="Розы", price=100)
        self.order = Order.objects.create(user=self.user, status="new")

    def test_order_creation(self):
        """Проверка создания заказа"""
        self.order.products.add(self.product)  # Добавляем товар в заказ
        self.assertEqual(self.order.user.username, "testuser")  # Проверяем, что пользователь указан верно
        self.assertEqual(self.order.status, "new")  # Проверяем, что статус заказа - "new"
        self.assertIn(self.product, self.order.products.all())  # Проверяем, что продукт добавлен в заказ

