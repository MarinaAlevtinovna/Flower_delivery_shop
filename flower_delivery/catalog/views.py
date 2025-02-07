from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer

def product_list(request):
    products = Product.objects.all()
    return render(request, "catalog/product_list.html", {"products": products})

class CatalogAPIView(APIView):
    permission_classes = [AllowAny]  # Доступ без токена

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)