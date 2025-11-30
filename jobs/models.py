from django.db import models
from django.utils import timezone
from employers.models import Employer

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_categories'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )
    
    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    )
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='mid')
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)
    
    application_deadline = models.DateField(null=True, blank=True)
    positions_available = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = f"{slugify(self.title)}-{uuid.uuid4().hex[:8]}"
        
        if self.is_active and not self.published_at:
            self.published_at = timezone.now()
        elif not self.is_active:
            self.published_at = None
            
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.application_deadline:
            return timezone.now().date() > self.application_deadline
        return False
    
    # @property
    # def applications_count(self):
    #     return self.applications.count()
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.2f} - {self.salary_max:,.2f}"
        elif self.salary_min:
            return f"From {self.salary_currency} {self.salary_min:,.2f}"
        return "Not specified"