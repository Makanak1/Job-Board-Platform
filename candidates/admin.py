from django.contrib import admin
from .models import Candidate, Resume

class ResumeInline(admin.TabularInline):
    model = Resume
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'location', 'experience_years', 'created_at')
    list_filter = ('experience_years', 'availability', 'created_at')
    search_fields = ('first_name', 'last_name', 'user__email', 'skills', 'location')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ResumeInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'profile_picture', 'phone')
        }),
        ('Professional Details', {
            'fields': ('bio', 'skills', 'experience_years', 'education')
        }),
        ('Location & Salary', {
            'fields': ('location', 'expected_salary_min', 'expected_salary_max', 'availability')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'candidate', 'is_primary', 'file_size', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('title', 'candidate__first_name', 'candidate__last_name')
    readonly_fields = ('uploaded_at', 'file_size')