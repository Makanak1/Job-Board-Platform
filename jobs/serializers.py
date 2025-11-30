from rest_framework import serializers
from .models import Job, JobCategory
from employers.serializers import EmployerListSerializer

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerListSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    salary_range = serializers.CharField(read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('employer', 'slug', 'views_count', 'published_at', 
                            'created_at', 'updated_at')
    
    def validate(self, attrs):
        if attrs.get('salary_min') and attrs.get('salary_max'):
            if attrs['salary_min'] > attrs['salary_max']:
                raise serializers.ValidationError({
                    "salary": "Minimum salary cannot be greater than maximum salary."
                })
        
        application_deadline = attrs.get('application_deadline')
        if application_deadline:
            from django.utils import timezone
            if application_deadline < timezone.now().date():
                raise serializers.ValidationError({
                    "application_deadline": "Deadline cannot be in the past."
                })
        
        return attrs

class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        exclude = ('employer', 'slug', 'views_count', 'published_at', 'created_at', 'updated_at')

class JobListSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    employer_logo = serializers.ImageField(source='employer.logo', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Job
        fields = ('id', 'title', 'slug', 'employer_name', 'employer_logo', 'category_name',
                'job_type', 'location', 'is_remote', 'salary_min', 'salary_max', 
                'salary_currency', 'is_active', 'is_featured', 'applications_count',
                'created_at', 'application_deadline')