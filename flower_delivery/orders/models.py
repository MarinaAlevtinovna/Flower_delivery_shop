from django.db import models
from users.models import CustomUser
from catalog.models import Product

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("completed", "Завершён"),
    ], default="new")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

