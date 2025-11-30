from django.db import models
from django.utils import timezone
from candidates.models import Candidate, Resume
from jobs.models import Job

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, related_name='applications')
    
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    employer_notes = models.TextField(blank=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'applications'
        ordering = ['-applied_at']
        unique_together = ('job', 'candidate')
        indexes = [
            models.Index(fields=['status', '-applied_at']),
            models.Index(fields=['job', 'status']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If updating
            old_status = Application.objects.get(pk=self.pk).status
            if old_status != self.status and self.status != 'pending':
                self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_status_history'
        ordering = ['-changed_at']
        verbose_name_plural = 'Application Status Histories'
    
    def __str__(self):
        return f"{self.application} - {self.old_status} -> {self.new_status}"