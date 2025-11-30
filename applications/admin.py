from django.contrib import admin
from .models import Application, ApplicationStatusHistory

class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('changed_at',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'applied_at', 'reviewed_at')
    list_filter = ('status', 'applied_at', 'reviewed_at')
    search_fields = ('candidate__first_name', 'candidate__last_name', 'job__title', 
                     'job__employer__company_name')
    readonly_fields = ('applied_at', 'updated_at', 'reviewed_at')
    inlines = [ApplicationStatusHistoryInline]
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'candidate', 'resume')
        }),
        ('Application Content', {
            'fields': ('cover_letter',)
        }),
        ('Status', {
            'fields': ('status', 'employer_notes')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'reviewed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_at')
    search_fields = ('application__candidate__first_name', 'application__job__title')
    readonly_fields = ('changed_at',)