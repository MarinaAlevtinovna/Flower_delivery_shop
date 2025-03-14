from django.db import models
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()


def get_products(self):
    Product = apps.get_model("catalog", "Product")
    return Product.objects.filter(order=self)
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField("catalog.Product")
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")

    status = models.CharField(max_length=50, choices=[
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("completed", "Завершён"),
    ], default="new")

    def __str__(self):
        return f"Заказ {self.id} от {self.name}"




