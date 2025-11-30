from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Candidate, Resume
from .serializers import (
    CandidateSerializer, 
    CandidateListSerializer, 
    ResumeSerializer
)
from .permissions import IsCandidateOwner
from applications.models import Application
from applications.serializers import ApplicationListSerializer
import PyPDF2
import docx

class CandidateListView(generics.ListAPIView):
    """
    List all candidates
    GET /api/candidates/
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    permission_classes = (permissions.AllowAny,)
    search_fields = ['first_name', 'last_name', 'skills', 'location']
    filterset_fields = ['experience_years', 'availability']

class CandidateDetailView(generics.RetrieveAPIView):
    """
    Get candidate details
    GET /api/candidates/{id}/
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = (permissions.AllowAny,)

class CandidateProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update candidate profile (own profile only)
    GET/PUT /api/candidates/profile/
    """
    serializer_class = CandidateSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        return get_object_or_404(Candidate, user=self.request.user)

class ResumeUploadView(generics.CreateAPIView):
    """
    Upload a new resume
    POST /api/candidates/resumes/upload/
    """
    serializer_class = ResumeSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        resume_file = self.request.FILES.get('file')
        
        # Extract text from resume
        extracted_text = self.extract_text_from_file(resume_file)
        
        serializer.save(
            candidate=candidate,
            file_size=resume_file.size,
            extracted_text=extracted_text
        )
    
    def extract_text_from_file(self, file):
        """Extract text from PDF or DOCX file"""
        text = ""
        try:
            if file.content_type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            elif file.content_type in ['application/msword', 
                                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                doc = docx.Document(file)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
        
        return text

class ResumeListView(generics.ListAPIView):
    """
    List candidate's resumes
    GET /api/candidates/resumes/
    """
    serializer_class = ResumeSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def get_queryset(self):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        return Resume.objects.filter(candidate=candidate)

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a resume
    GET/PUT/DELETE /api/candidates/resumes/{id}/
    """
    serializer_class = ResumeSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def get_queryset(self):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        return Resume.objects.filter(candidate=candidate)

class CandidateApplicationsView(generics.ListAPIView):
    """
    List candidate's applications
    GET /api/candidates/applications/
    """
    serializer_class = ApplicationListSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def get_queryset(self):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        return Application.objects.filter(candidate=candidate)

class CandidateStatsView(APIView):
    """
    Get candidate statistics
    GET /api/candidates/stats/
    """
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def get(self, request):
        candidate = get_object_or_404(Candidate, user=request.user)
        
        applications = Application.objects.filter(candidate=candidate)
        total_applications = applications.count()
        pending = applications.filter(status='pending').count()
        under_review = applications.filter(status='under_review').count()
        shortlisted = applications.filter(status='shortlisted').count()
        rejected = applications.filter(status='rejected').count()
        hired = applications.filter(status='hired').count()
        
        return Response({
            'total_applications': total_applications,
            'pending': pending,
            'under_review': under_review,
            'shortlisted': shortlisted,
            'rejected': rejected,
            'hired': hired,
            'total_resumes': candidate.resumes.count(),
        })