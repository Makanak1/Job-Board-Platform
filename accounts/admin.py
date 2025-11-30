from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_email_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_email_verified', 'created_at')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'is_email_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'email')}),
    )