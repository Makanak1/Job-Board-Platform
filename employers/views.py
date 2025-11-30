from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Employer
from .serializers import EmployerSerializer, EmployerListSerializer
from .permissions import IsEmployerOwner
from jobs.models import Job
from django.db.models import Count
from jobs.serializers import JobListSerializer

class EmployerListView(generics.ListAPIView):
    """
    List all employers
    GET /api/employers/
    """
    queryset = Employer.objects.all()
    serializer_class = EmployerListSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_fields = ['industry', 'company_size', 'is_verified']
    search_fields = ['company_name', 'description', 'location']

class EmployerDetailView(generics.RetrieveAPIView):
    """
    Get employer details
    GET /api/employers/{id}/
    """
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = (permissions.AllowAny,)

class EmployerProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update employer profile (own profile only)
    GET/PUT /api/employers/profile/
    """
    serializer_class = EmployerSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def get_object(self):
        return get_object_or_404(Employer, user=self.request.user)

class EmployerJobsView(generics.ListAPIView):
    """
    List jobs posted by the employer
    GET /api/employers/my-jobs/
    """
    serializer_class = JobListSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def get_queryset(self):
        employer = get_object_or_404(Employer, user=self.request.user)
        return Job.objects.filter(employer=employer).annotate(
            applications_count=Count('applications')  # Add annotation

        )
class EmployerStatsView(APIView):
    """
    Get employer statistics
    GET /api/employers/stats/
    """
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def get(self, request):
        employer = get_object_or_404(Employer, user=request.user)
        
        total_jobs = employer.jobs.count()
        active_jobs = employer.jobs.filter(is_active=True).count()
        total_applications = sum(job.applications.count() for job in employer.jobs.all())
        pending_applications = sum(
            job.applications.filter(status='pending').count() 
            for job in employer.jobs.all()
        )
        
        return Response({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
        })