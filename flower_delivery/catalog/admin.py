from django.contrib import admin
from django.apps import apps
Product = apps.get_model("catalog", "Product")

admin.site.register(Product)

