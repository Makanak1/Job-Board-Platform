from django.contrib import admin
from .models import Job, JobCategory

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'job_type', 'location', 'is_active', 
                    'views_count', 'applications_count', 'created_at')
    list_filter = ('is_active', 'is_featured', 'job_type', 'experience_level', 'category', 'created_at')
    search_fields = ('title', 'description', 'employer__company_name', 'location')
    readonly_fields = ('slug', 'views_count', 'published_at', 'created_at', 'updated_at', 'applications_count')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employer', 'title', 'slug', 'category', 'job_type', 'experience_level')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency')
        }),
        ('Location & Remote', {
            'fields': ('location', 'is_remote')
        }),
        ('Application Details', {
            'fields': ('application_deadline', 'positions_available')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'views_count', 'applications_count')
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applications_count(self, obj):
        return obj.applications.count()
    applications_count.short_description = 'Applications'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        qs = super().get_queryset(request)
        return qs.select_related('employer', 'category').annotate(
            applications_count=Count('applications')
        )