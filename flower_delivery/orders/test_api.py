from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from catalog.models import Product
from orders.models import Order
from rest_framework.authtoken.models import Token

class OrderAPITest(APITestCase):
    def setUp(self):
        """Создаём тестовые данные"""
        self.user = CustomUser.objects.create(username="testuser", email="test@example.com", password="testpass")
        self.token = Token.objects.create(user=self.user)  # Генерируем API токен
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")  # Добавляем авторизацию

        self.product = Product.objects.create(name="Лилии", price=150)
        self.order_data = {
            "user": self.user.id,
            "products": [self.product.id],
            "status": "new",
            "name": "Иван",
            "phone": "89111234567",
            "address": "ул. Пушкина, д.10"
        }

    def test_create_order(self):
        """Тестирование создания заказа через API"""
        response = self.client.post("/api/orders/", self.order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Проверяем код 201 (успешно создано)
        self.assertEqual(Order.objects.count(), 1)  # Проверяем, что заказ создался

    def test_get_orders(self):
        """Тестирование получения списка заказов"""
        Order.objects.create(user=self.user, status="new")
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Проверяем, что ответ успешный
        self.assertGreater(len(response.json()), 0)  # Проверяем, что в ответе есть заказы
