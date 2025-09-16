from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "phone", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
