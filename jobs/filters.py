import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    job_type = django_filters.ChoiceFilter(choices=Job.JOB_TYPE_CHOICES)
    experience_level = django_filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVEL_CHOICES)
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    is_remote = django_filters.BooleanFilter()
    category = django_filters.CharFilter(field_name='category__slug')
    employer = django_filters.NumberFilter(field_name='employer__id')

    class Meta:
        model = Job
        fields = ['title', 'location', 'job_type', 'experience_level', 
            'salary_min', 'salary_max', 'is_remote', 'category', 'employer']