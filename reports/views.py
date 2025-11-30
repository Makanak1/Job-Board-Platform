from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse

from jobs.models import Job
from applications.models import Application
from candidates.models import Candidate
from employers.models import Employer
from accounts.permissions import IsAdminUser

class PlatformStatsView(APIView):
    """
    Get overall platform statistics
    GET /api/reports/platform-stats/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        # Date ranges
        today = timezone.now()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)
        
        stats = {
            'users': {
                'total': Candidate.objects.count() + Employer.objects.count(),
                'candidates': Candidate.objects.count(),
                'employers': Employer.objects.count(),
                'candidates_last_30_days': Candidate.objects.filter(created_at__gte=last_30_days).count(),
                'employers_last_30_days': Employer.objects.filter(created_at__gte=last_30_days).count(),
            },
            'jobs': {
                'total': Job.objects.count(),
                'active': Job.objects.filter(is_active=True).count(),
                'inactive': Job.objects.filter(is_active=False).count(),
                'posted_last_30_days': Job.objects.filter(created_at__gte=last_30_days).count(),
                'by_type': list(Job.objects.values('job_type').annotate(count=Count('id'))),
            },
            'applications': {
                'total': Application.objects.count(),
                'pending': Application.objects.filter(status='pending').count(),
                'under_review': Application.objects.filter(status='under_review').count(),
                'shortlisted': Application.objects.filter(status='shortlisted').count(),
                'hired': Application.objects.filter(status='hired').count(),
                'rejected': Application.objects.filter(status='rejected').count(),
                'last_30_days': Application.objects.filter(applied_at__gte=last_30_days).count(),
                'last_7_days': Application.objects.filter(applied_at__gte=last_7_days).count(),
            }
        }
        
        return Response(stats)

class JobAnalyticsView(APIView):
    """
    Get detailed job analytics
    GET /api/reports/job-analytics/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        # Most applied jobs
        most_applied_jobs = Job.objects.annotate(
            app_count=Count('applications')
        ).order_by('-app_count')[:10]
        
        # Jobs by category
        jobs_by_category = Job.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average applications per job
        avg_applications = Application.objects.values('job').annotate(
            count=Count('id')
        ).aggregate(avg=Avg('count'))
        
        # Application trends (monthly)
        monthly_trends = Application.objects.annotate(
            month=TruncMonth('applied_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Weekly trends
        weekly_trends = Application.objects.annotate(
            week=TruncWeek('applied_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')[:12]  # Last 12 weeks
        
        data = {
            'most_applied_jobs': [
                {
                    'id': job.id,
                    'title': job.title,
                    'company': job.employer.company_name,
                    'applications': job.app_count,
                    'location': job.location
                }
                for job in most_applied_jobs
            ],
            'jobs_by_category': list(jobs_by_category),
            'avg_applications_per_job': round(avg_applications['avg'] or 0, 2),
            'monthly_application_trends': list(monthly_trends),
            'weekly_application_trends': list(weekly_trends)
        }
        
        return Response(data)

class EmployerAnalyticsView(APIView):
    """
    Get employer analytics
    GET /api/reports/employer-analytics/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        # Most active employers
        active_employers = Employer.objects.annotate(
            job_count=Count('jobs'),
            active_job_count=Count('jobs', filter=Q(jobs__is_active=True)),
            total_applications=Count('jobs__applications')
        ).order_by('-job_count')[:10]
        
        # Employers by industry
        employers_by_industry = Employer.objects.values('industry').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Verified vs unverified employers
        verification_stats = {
            'verified': Employer.objects.filter(is_verified=True).count(),
            'unverified': Employer.objects.filter(is_verified=False).count()
        }
        
        data = {
            'most_active_employers': [
                {
                    'id': emp.id,
                    'company_name': emp.company_name,
                    'total_jobs': emp.job_count,
                    'active_jobs': emp.active_job_count,
                    'total_applications': emp.total_applications,
                    'location': emp.location,
                    'is_verified': emp.is_verified
                }
                for emp in active_employers
            ],
            'employers_by_industry': list(employers_by_industry),
            'verification_stats': verification_stats
        }
        
        return Response(data)

class CandidateAnalyticsView(APIView):
    """
    Get candidate analytics
    GET /api/reports/candidate-analytics/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        # Candidates by experience level
        candidates_by_experience = Candidate.objects.values('experience_years').annotate(
            count=Count('id')
        ).order_by('experience_years')
        
        # Most active candidates (by application count)
        active_candidates = Candidate.objects.annotate(
            application_count=Count('applications')
        ).filter(application_count__gt=0).order_by('-application_count')[:10]
        
        # Candidate registration trends
        registration_trends = Candidate.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        data = {
            'candidates_by_experience': list(candidates_by_experience),
            'most_active_candidates': [
                {
                    'id': c.id,
                    'name': c.full_name,
                    'location': c.location,
                    'applications': c.application_count,
                    'experience_years': c.experience_years
                }
                for c in active_candidates
            ],
            'registration_trends': list(registration_trends)
        }
        
        return Response(data)

class ApplicationAnalyticsView(APIView):
    """
    Get application analytics
    GET /api/reports/application-analytics/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        # Application status distribution
        status_distribution = Application.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average time to hire (from application to hired status)
        # This is a simplified calculation
        hired_apps = Application.objects.filter(status='hired')
        
        # Applications by job type
        apps_by_job_type = Application.objects.values('job__job_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        data = {
            'status_distribution': list(status_distribution),
            'total_hired': hired_apps.count(),
            'applications_by_job_type': list(apps_by_job_type)
        }
        
        return Response(data)

class ExportApplicationsView(APIView):
    """
    Export applications to CSV
    GET /api/reports/export-applications/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Application ID', 
            'Candidate Name', 
            'Candidate Email',
            'Candidate Phone',
            'Job Title', 
            'Company', 
            'Job Location',
            'Status', 
            'Applied Date',
            'Last Updated'
        ])
        
        applications = Application.objects.select_related(
            'candidate', 'candidate__user', 'job', 'job__employer'
        ).all()
        
        for app in applications:
            writer.writerow([
                app.id,
                app.candidate.full_name,
                app.candidate.user.email,
                app.candidate.phone or 'N/A',
                app.job.title,
                app.job.employer.company_name,
                app.job.location,
                app.get_status_display(),
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                app.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

class ExportJobsView(APIView):
    """
    Export jobs to CSV
    GET /api/reports/export-jobs/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jobs_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Job ID', 
            'Title', 
            'Company', 
            'Category', 
            'Job Type',
            'Experience Level',
            'Location', 
            'Is Remote',
            'Salary Min',
            'Salary Max',
            'Applications', 
            'Views', 
            'Status', 
            'Created Date',
            'Application Deadline'
        ])
        
        jobs = Job.objects.select_related('employer', 'category').annotate(
            app_count=Count('applications')
        ).all()
        
        for job in jobs:
            writer.writerow([
                job.id,
                job.title,
                job.employer.company_name,
                job.category.name if job.category else 'N/A',
                job.get_job_type_display(),
                job.get_experience_level_display(),
                job.location,
                'Yes' if job.is_remote else 'No',
                job.salary_min or 'N/A',
                job.salary_max or 'N/A',
                job.app_count,
                job.views_count,
                'Active' if job.is_active else 'Inactive',
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else 'N/A'
            ])
        
        return response

class ExportCandidatesView(APIView):
    """
    Export candidates to CSV
    GET /api/reports/export-candidates/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="candidates_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Candidate ID',
            'Full Name',
            'Email',
            'Phone',
            'Location',
            'Experience Years',
            'Skills',
            'Applications Count',
            'Registration Date'
        ])
        
        candidates = Candidate.objects.select_related('user').annotate(
            app_count=Count('applications')
        ).all()
        
        for candidate in candidates:
            writer.writerow([
                candidate.id,
                candidate.full_name,
                candidate.user.email,
                candidate.phone or 'N/A',
                candidate.location,
                candidate.experience_years,
                candidate.skills[:100] if candidate.skills else 'N/A',  # Truncate skills
                candidate.app_count,
                candidate.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

class ExportEmployersView(APIView):
    """
    Export employers to CSV
    GET /api/reports/export-employers/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employer ID',
            'Company Name',
            'Contact Email',
            'Website',
            'Location',
            'Industry',
            'Company Size',
            'Is Verified',
            'Total Jobs',
            'Active Jobs',
            'Registration Date'
        ])
        
        employers = Employer.objects.select_related('user').annotate(
            total_jobs=Count('jobs'),
            active_jobs=Count('jobs', filter=Q(jobs__is_active=True))
        ).all()
        
        for employer in employers:
            writer.writerow([
                employer.id,
                employer.company_name,
                employer.contact_email,
                employer.website or 'N/A',
                employer.location,
                employer.industry,
                employer.company_size,
                'Yes' if employer.is_verified else 'No',
                employer.total_jobs,
                employer.active_jobs,
                employer.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

class DashboardStatsView(APIView):
    """
    Get comprehensive dashboard statistics
    GET /api/reports/dashboard/
    """
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)
    
    def get(self, request):
        today = timezone.now()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)
        yesterday = today - timedelta(days=1)
        
        # Get counts
        total_users = Candidate.objects.count() + Employer.objects.count()
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        total_applications = Application.objects.count()
        
        # Growth metrics
        new_users_today = (
            Candidate.objects.filter(created_at__date=today.date()).count() +
            Employer.objects.filter(created_at__date=today.date()).count()
        )
        new_jobs_today = Job.objects.filter(created_at__date=today.date()).count()
        new_applications_today = Application.objects.filter(applied_at__date=today.date()).count()
        
        # Calculate growth percentages
        users_yesterday = (
            Candidate.objects.filter(created_at__date=yesterday.date()).count() +
            Employer.objects.filter(created_at__date=yesterday.date()).count()
        )
        user_growth = ((new_users_today - users_yesterday) / users_yesterday * 100) if users_yesterday > 0 else 0
        
        data = {
            'overview': {
                'total_users': total_users,
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'total_applications': total_applications,
            },
            'today': {
                'new_users': new_users_today,
                'new_jobs': new_jobs_today,
                'new_applications': new_applications_today,
            },
            'growth': {
                'user_growth_percentage': round(user_growth, 2),
            },
            'recent_activity': {
                'users_last_7_days': (
                    Candidate.objects.filter(created_at__gte=last_7_days).count() +
                    Employer.objects.filter(created_at__gte=last_7_days).count()
                ),
                'jobs_last_7_days': Job.objects.filter(created_at__gte=last_7_days).count(),
                'applications_last_7_days': Application.objects.filter(applied_at__gte=last_7_days).count(),
            }
        }
        
        return Response(data)