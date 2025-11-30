from django.contrib import admin
from .models import Employer

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'contact_email', 'location', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'industry', 'company_size', 'created_at')
    search_fields = ('company_name', 'user__email', 'contact_email', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'company_name', 'description', 'logo')
        }),
        ('Contact Details', {
            'fields': ('contact_email', 'website', 'location')
        }),
        ('Company Details', {
            'fields': ('industry', 'company_size', 'founded_year')
        }),
        ('Status', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )