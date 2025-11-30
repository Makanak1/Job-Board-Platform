from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobCategory
from .serializers import (
    JobSerializer, 
    JobListSerializer, 
    JobCreateUpdateSerializer,
    JobCategorySerializer
)
from .filters import JobFilter
from employers.models import Employer
from employers.permissions import IsEmployerOwner

class JobCategoryListView(generics.ListAPIView):
    """
    List all job categories
    GET /api/jobs/categories/
    """
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = (permissions.AllowAny,)

class JobListView(generics.ListAPIView):
    """
    List all active jobs with search and filters
    GET /api/jobs/
    """
    serializer_class = JobListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'requirements', 'employer__company_name']
    ordering_fields = ['created_at', 'salary_min', 'application_deadline', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).select_related(
            'employer', 'category'
        ).annotate(
            applications_count=Count('applications')
        )
        return queryset

class JobDetailView(generics.RetrieveAPIView):
    """
    Get job details and increment view count
    GET /api/jobs/{slug}/
    """
    serializer_class = JobSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'
    
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related(
            'employer', 'category'
        ).annotate(
            applications_count=Count('applications')  # Add annotation here
        )
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class JobCreateView(generics.CreateAPIView):
    """
    Create a new job (employers only)
    POST /api/jobs/create/
    """
    serializer_class = JobCreateUpdateSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def perform_create(self, serializer):
        employer = get_object_or_404(Employer, user=self.request.user)
        serializer.save(employer=employer)

class JobUpdateView(generics.UpdateAPIView):
    """
    Update a job (owner only)
    PUT/PATCH /api/jobs/{slug}/update/
    """
    serializer_class = JobCreateUpdateSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    lookup_field = 'slug'
    
    def get_queryset(self):
        employer = get_object_or_404(Employer, user=self.request.user)
        return Job.objects.filter(employer=employer)

class JobDeleteView(generics.DestroyAPIView):
    """
    Delete a job (owner only)
    DELETE /api/jobs/{slug}/delete/
    """
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    lookup_field = 'slug'
    
    def get_queryset(self):
        employer = get_object_or_404(Employer, user=self.request.user)
        return Job.objects.filter(employer=employer)

class JobToggleActiveView(APIView):
    """
    Toggle job active status
    POST /api/jobs/{slug}/toggle-active/
    """
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def post(self, request, slug):
        employer = get_object_or_404(Employer, user=request.user)
        job = get_object_or_404(Job, slug=slug, employer=employer)
        
        job.is_active = not job.is_active
        job.save()
        
        return Response({
            'message': f"Job {'activated' if job.is_active else 'deactivated'} successfully",
            'is_active': job.is_active
        })

class JobSearchView(APIView):
    """
    Advanced job search
    GET /api/jobs/search/
    """
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        queryset = Job.objects.filter(is_active=True)
        
        # Keyword search
        keyword = request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(requirements__icontains=keyword) |
                Q(employer__company_name__icontains=keyword)
            )
        
        # Location search
        location = request.query_params.get('location', '')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Category filter
        category = request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Job type filter
        job_type = request.query_params.get('job_type', '')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Salary range filter
        min_salary = request.query_params.get('min_salary', '')
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)
        
        max_salary = request.query_params.get('max_salary', '')
        if max_salary:
            queryset = queryset.filter(salary_max__lte=max_salary)
        
        # Remote filter
        is_remote = request.query_params.get('is_remote', '')
        if is_remote:
            queryset = queryset.filter(is_remote=is_remote.lower() == 'true')
        
        # Ordering
        order_by = request.query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        
        # Add annotation before serializing
        queryset = queryset.annotate(applications_count=Count('applications'))
        
        # Pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(queryset, request)
        
        serializer = JobListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)