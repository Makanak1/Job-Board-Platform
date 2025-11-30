from django.db import models
from django.conf import settings

def profile_picture_path(instance, filename):
    return f'profile_pictures/{instance.user.id}/{filename}'

def resume_path(instance, filename):
    return f'resumes/{instance.candidate.user.id}/{filename}'

class Candidate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_path, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    experience_years = models.IntegerField(default=0)
    education = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    expected_salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'candidates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=resume_path)
    extracted_text = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    file_size = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other resumes for this candidate to non-primary
            Resume.objects.filter(candidate=self.candidate, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)