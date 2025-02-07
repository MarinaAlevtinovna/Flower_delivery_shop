from django.urls import path
from .views import product_list, CatalogAPIView

urlpatterns = [
    path('catalog/', product_list, name='catalog'),
    path("api/catalog/", CatalogAPIView.as_view(), name='catalog-api')
]