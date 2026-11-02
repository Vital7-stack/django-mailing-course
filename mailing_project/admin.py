from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(BaseUserAdmin):
    list_display = (*BaseUserAdmin.list_display, 'is_active')
    list_filter = (*BaseUserAdmin.list_filter, 'is_active')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)