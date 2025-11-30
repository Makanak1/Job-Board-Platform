from rest_framework import serializers
from .models import Candidate, Resume
from accounts.serializers import UserSerializer

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('candidate', 'extracted_text', 'file_size', 'uploaded_at')
    
    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Resume file size cannot exceed 5MB.")
        
        allowed_types = ['application/pdf', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only PDF, DOC and DOCX files are allowed.")
        
        return value

class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    resumes = ResumeSerializer(many=True, read_only=True)
    skills_list = serializers.ListField(read_only=True)
    
    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def validate_profile_picture(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:  # 2MB limit
                raise serializers.ValidationError("Profile picture cannot exceed 2MB.")
            
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only JPEG, JPG and PNG images are allowed.")
        
        return value

class CandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        exclude = ('user', 'created_at', 'updated_at')

class CandidateListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Candidate
        fields = ('id', 'full_name', 'profile_picture', 'location', 
                'experience_years', 'availability')