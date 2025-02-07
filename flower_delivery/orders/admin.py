from django.contrib import admin
from .models import Order
from django.utils.html import format_html

# admin.site.register(Order)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Улучшаем отображение заказов в Django Admin"""

    list_display = ("id", "user_link", "formatted_products", "colored_status", "created_at")  # Улучшаем список полей
    list_filter = ("status", "created_at")  # Добавляем фильтры
    search_fields = ("id", "user__username", "phone")  # Добавляем поиск

    def user_link(self, obj):
        """Делаем имя пользователя кликабельным"""
        return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', obj.user.id, obj.user.username)

    user_link.short_description = "Пользователь"

    def formatted_products(self, obj):
        """Отображает список товаров вместо ID"""
        return ", ".join([p.name for p in obj.products.all()])

    formatted_products.short_description = "Товары"

    def colored_status(self, obj):
        """Отображает статус заказа цветным текстом"""
        status_colors = {
            "new": "🟡 Новый",
            "processing": "🟠 В обработке",
            "completed": "🟢 Завершён"
        }
        return status_colors.get(obj.status, "❓ Неизвестный статус")

    colored_status.short_description = "Статус"

