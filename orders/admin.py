from django.contrib import admin
from . import models
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'email', 'paid', 'created_at']
    inlines = [OrderItemInline]