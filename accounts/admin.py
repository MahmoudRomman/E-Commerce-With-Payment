from django.contrib import admin
from . import models
# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "username"]
    search_fields = ["username"]



admin.site.register(models.Account, AccountAdmin)

