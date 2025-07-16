import site
from django.contrib import admin
from . import models
# Register your models here.



class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Product, ProductAdmin)