from django.db import models
from django.conf import settings
from django.core.validators import URLValidator

def company_logo_path(instance, filename):
    return f'company_logos/{instance.user.id}/{filename}'

class Employer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(max_length=500, blank=True, validators=[URLValidator()])
    contact_email = models.EmailField()
    logo = models.ImageField(upload_to=company_logo_path, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    founded_year = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employers'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.company_name
    
    @property
    def total_jobs(self):
        return self.jobs.count()
    
    @property
    def active_jobs(self):
        return self.jobs.filter(is_active=True).count()