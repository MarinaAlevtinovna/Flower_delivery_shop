from rest_framework import serializers
from django.apps import apps

Order = apps.get_model("orders", "Order")
Product = apps.get_model("catalog", "Product")

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
