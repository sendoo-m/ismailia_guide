from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'phone', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('معلومات إضافية', {
            'fields': ('user_type', 'phone', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('user_type', 'phone', 'email')
        }),
    )
