from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_blocked')
    list_filter = ('role', 'is_blocked')
    search_fields = ('user__username', 'user__email')
