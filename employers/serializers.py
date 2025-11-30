from rest_framework import serializers
from .models import Employer
from accounts.serializers import UserSerializer

class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_jobs = serializers.IntegerField(read_only=True)
    active_jobs = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Employer
        fields = '__all__'
        read_only_fields = ('user', 'is_verified', 'created_at', 'updated_at')

def validate_logo(self, value):
    if value:
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Logo file size cannot exceed 5MB.")
        
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG, JPG and PNG images are allowed.")
    
    return value

class EmployerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        exclude = ('user', 'is_verified', 'created_at', 'updated_at')
    
class EmployerListSerializer(serializers.ModelSerializer):
    total_jobs = serializers.IntegerField(read_only=True)
    active_jobs = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Employer
        fields = ('id', 'company_name', 'logo', 'location', 'industry', 
            'total_jobs', 'active_jobs', 'is_verified')