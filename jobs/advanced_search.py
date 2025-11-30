from django.db.models import Q, Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Job
from .serializers import JobListSerializer

class AdvancedJobSearchView(APIView):
    """
    Advanced job search with multiple filters and sorting
    GET /api/jobs/advanced-search/
    """
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        queryset = Job.objects.filter(is_active=True).select_related('employer', 'category')
        
        # Text search across multiple fields
        search_query = request.query_params.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query) |
                Q(employer__company_name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Location filter with multiple locations
        locations = request.query_params.getlist('locations[]')
        if locations:
            location_query = Q()
            for location in locations:
                location_query |= Q(location__icontains=location)
            queryset = queryset.filter(location_query)
        
        # Multiple categories
        categories = request.query_params.getlist('categories[]')
        if categories:
            queryset = queryset.filter(category__slug__in=categories)
        
        # Multiple job types
        job_types = request.query_params.getlist('job_types[]')
        if job_types:
            queryset = queryset.filter(job_type__in=job_types)
        
        # Experience level
        experience_levels = request.query_params.getlist('experience_levels[]')
        if experience_levels:
            queryset = queryset.filter(experience_level__in=experience_levels)
        
        # Salary range
        min_salary = request.query_params.get('min_salary')
        max_salary = request.query_params.get('max_salary')
        
        if min_salary:
            queryset = queryset.filter(
                Q(salary_min__gte=min_salary) | Q(salary_min__isnull=True)
            )
        
        if max_salary:
            queryset = queryset.filter(
                Q(salary_max__lte=max_salary) | Q(salary_max__isnull=True)
            )
        
        # Remote jobs only
        remote_only = request.query_params.get('remote_only', '').lower() == 'true'
        if remote_only:
            queryset = queryset.filter(is_remote=True)
        
        # Featured jobs only
        featured_only = request.query_params.get('featured_only', '').lower() == 'true'
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        # Posted within days
        posted_within = request.query_params.get('posted_within')
        if posted_within:
            from django.utils import timezone
            from datetime import timedelta
            days = int(posted_within)
            date_from = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=date_from)
        
        # Company filter
        companies = request.query_params.getlist('companies[]')
        if companies:
            queryset = queryset.filter(employer__id__in=companies)
        
        # Annotate with applications count
        queryset = queryset.annotate(applications_count=Count('applications'))
        
        # Sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        valid_sort_fields = [
            'created_at', '-created_at',
            'salary_min', '-salary_min',
            'salary_max', '-salary_max',
            'title', '-title',
            'application_deadline', '-application_deadline',
            'views_count', '-views_count',
            'applications_count', '-applications_count'
        ]
        
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        
        # Pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        result_page = paginator.paginate_queryset(queryset, request)
        
        serializer = JobListSerializer(result_page, many=True)
        
        # Add aggregation data
        response_data = paginator.get_paginated_response(serializer.data).data
        response_data['aggregations'] = {
            'total_results': queryset.count(),
            'categories': self.get_category_facets(queryset),
            'job_types': self.get_job_type_facets(queryset),
            'locations': self.get_location_facets(queryset),
        }
        
        return Response(response_data)
    
    def get_category_facets(self, queryset):
        """Get job counts by category"""
        return list(queryset.values('category__name', 'category__slug')
                .annotate(count=Count('id'))
                .order_by('-count')[:10])
    
    def get_job_type_facets(self, queryset):
        """Get job counts by type"""
        return list(queryset.values('job_type')
                .annotate(count=Count('id'))
                .order_by('-count'))
    
    def get_location_facets(self, queryset):
        """Get job counts by location"""
        return list(queryset.values('location')
                .annotate(count=Count('id'))
                .order_by('-count')[:10])