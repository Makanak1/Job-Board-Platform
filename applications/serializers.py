from rest_framework import serializers
from .models import Application, ApplicationStatusHistory
from candidates.serializers import CandidateListSerializer, ResumeSerializer
from jobs.serializers import JobListSerializer

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    candidate = CandidateListSerializer(read_only=True)
    job = JobListSerializer(read_only=True)
    resume = ResumeSerializer(read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('applied_at', 'updated_at', 'reviewed_at')

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('job', 'resume', 'cover_letter')
    
    def validate(self, attrs):
        job = attrs.get('job')
        candidate = self.context['request'].user.candidate_profile
        
        # Check if already applied
        if Application.objects.filter(job=job, candidate=candidate).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        
        # Check if job is active
        if not job.is_active:
            raise serializers.ValidationError("This job is no longer accepting applications.")
        
        # Check if deadline passed
        if job.is_expired:
            raise serializers.ValidationError("The application deadline has passed.")
        
        # Validate resume belongs to candidate
        resume = attrs.get('resume')
        if resume and resume.candidate != candidate:
            raise serializers.ValidationError("Invalid resume selected.")
        
        return attrs

class ApplicationUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('status', 'employer_notes')
    
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {', '.join(valid_statuses)}")
        return value

class ApplicationListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    candidate_email = serializers.EmailField(source='candidate.user.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.employer.company_name', read_only=True)
    
    class Meta:
        model = Application
        fields = ('id', 'candidate_name', 'candidate_email', 'job_title', 
                'company_name', 'status', 'applied_at', 'reviewed_at')