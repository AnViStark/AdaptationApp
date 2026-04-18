from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Адаптация Targem', {
            'fields': ('role', 'department', 'project', 'start_date', 'points', 'level'),
        }),
    )
    list_display = ('username', 'get_full_name', 'role', 'department', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
