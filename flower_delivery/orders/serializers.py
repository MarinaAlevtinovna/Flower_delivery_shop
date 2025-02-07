from rest_framework import serializers
from .models import Order, Product
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Product
        fields = ["id", "name", "price", "image"]

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created_at = serializers.DateTimeField(read_only=True)  # ✅ Добавляем это поле

    class Meta:
        model = Order
        fields = ["id", "user", "products", "status", "name", "phone", "address", "created_at"]

    def create(self, validated_data):
        products = validated_data.pop("products", [])
        order = Order.objects.create(**validated_data)
        order.products.set(products)
        return order


