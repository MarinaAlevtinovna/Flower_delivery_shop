from django.contrib import admin
from .models import Order
from django.utils.html import format_html

# admin.site.register(Order)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "formatted_products", "colored_status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "phone")

    def user_link(self, obj):
        return format_html('<a href="/admin/users/customuser/{}/change/">{}</a>', obj.user.id, obj.user.username)

    user_link.short_description = "Пользователь"

    def formatted_products(self, obj):
        return ", ".join([p.name for p in obj.products.all()])

    formatted_products.short_description = "Товары"

    def colored_status(self, obj):
        status_colors = {
            "new": "🟡 Новый",
            "processing": "🟠 В обработке",
            "completed": "🟢 Завершён"
        }
        return status_colors.get(obj.status, "❓ Неизвестный статус")

    colored_status.short_description = "Статус"

