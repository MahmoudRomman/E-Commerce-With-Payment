import csv
from django.http import HttpResponse
from django.contrib import admin
from . import models
from django.urls import reverse
from django.utils.safestring import mark_safe
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem


def export_orders_to_csv(modeladmin, request, queryset):
    """Admin action to export selected orders to a CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    # Write header
    writer.writerow([
        'Order ID', 'User', 'First Name', 'Last Name', 'Email',
        'Address', 'City', 'Postal Code', 'Paid', 'Created At'
    ])

    # Write order data
    for order in queryset:
        writer.writerow([
            order.order_id,
            str(order.user) if order.user else 'Anonymous',
            order.first_name,
            order.last_name,
            order.email,
            order.address,
            order.city,
            order.postal_code,
            order.paid,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return response

export_orders_to_csv.short_description = "Export Selected Orders to CSV"



def order_pdf(obj):
    url = reverse("orders:admin_order_pdf", args=[obj.order_id])
    return mark_safe(f'<a href="{url}" target="_blank">PDF</a>')

order_pdf.short_description = "Invoice"

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'email', 'paid', 'created_at', order_pdf]
    inlines = [OrderItemInline]
    actions = [export_orders_to_csv]
