from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)
from employers.models import Employer
from employers.serializers import EmployerCreateSerializer
from candidates.models import Candidate
from candidates.serializers import CandidateCreateSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user (Employer or Candidate)
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        user_type = request.data.get('user_type')
        
        # Create profile based on user type
        if user_type == 'employer':
            employer_data = request.data.get('employer_profile', {})
            employer_serializer = EmployerCreateSerializer(data=employer_data)
            if employer_serializer.is_valid(raise_exception=True):
                employer_serializer.save(user=user)
        
        elif user_type == 'candidate':
            candidate_data = request.data.get('candidate_profile', {})
            candidate_serializer = CandidateCreateSerializer(data=candidate_data)
            if candidate_serializer.is_valid(raise_exception=True):
                candidate_serializer.save(user=user)
        
        headers = self.get_success_headers(user_serializer.data)
        return Response({
            'user': user_serializer.data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED, headers=headers)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login and obtain JWT tokens
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile
    GET/PUT /api/auth/profile/
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    """
    Change user password
    POST /api/auth/change-password/
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.data.get('old_password')):
                return Response({
                    'old_password': ['Wrong password.']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({
                'message': 'Password updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)