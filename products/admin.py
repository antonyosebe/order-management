from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock_quantity", "is_active")
    search_fields = ("name", "sku", "description")
    list_filter = ("is_active", "is_featured", "is_digital")
