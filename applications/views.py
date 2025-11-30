from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Application, ApplicationStatusHistory
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateStatusSerializer,
    ApplicationListSerializer
)
from candidates.models import Candidate
from candidates.permissions import IsCandidateOwner
from employers.models import Employer
from employers.permissions import IsEmployerOwner
from jobs.models import Job
from notifications.utils import send_application_notification

class ApplicationCreateView(generics.CreateAPIView):
    """
    Apply to a job
    POST /api/applications/apply/
    """
    serializer_class = ApplicationCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def perform_create(self, serializer):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        application = serializer.save(candidate=candidate, status='pending')
        
        # Send notification to employer
        send_application_notification(application, 'new')

class ApplicationDetailView(generics.RetrieveAPIView):
    """
    Get application details
    GET /api/applications/{id}/
    """
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'candidate':
            candidate = get_object_or_404(Candidate, user=user)
            return Application.objects.filter(candidate=candidate)
        elif user.user_type == 'employer':
            employer = get_object_or_404(Employer, user=user)
            return Application.objects.filter(job__employer=employer)
        return Application.objects.none()

class ApplicationUpdateStatusView(generics.UpdateAPIView):
    """
    Update application status (employers only)
    PATCH /api/applications/{id}/update-status/
    """
    serializer_class = ApplicationUpdateStatusSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def get_queryset(self):
        employer = get_object_or_404(Employer, user=self.request.user)
        return Application.objects.filter(job__employer=employer)
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        application = serializer.save()
        
        # Create status history
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=old_status,
            new_status=application.status,
            changed_by=self.request.user,
            notes=serializer.validated_data.get('employer_notes', '')
        )
        
        # Send notification to candidate
        send_application_notification(application, 'status_update')

class CandidateApplicationListView(generics.ListAPIView):
    """
    List candidate's applications
    GET /api/applications/my-applications/
    """
    serializer_class = ApplicationListSerializer
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def get_queryset(self):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        return Application.objects.filter(candidate=candidate).select_related(
            'job', 'job__employer', 'resume'
        )

class EmployerApplicationListView(generics.ListAPIView):
    """
    List applications for employer's jobs
    GET /api/applications/received/
    """
    serializer_class = ApplicationListSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    filterset_fields = ['status', 'job']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        employer = get_object_or_404(Employer, user=self.request.user)
        return Application.objects.filter(job__employer=employer).select_related(
            'candidate', 'candidate__user', 'job', 'resume'
        )

class JobApplicationsView(generics.ListAPIView):
    """
    List applications for a specific job (employer only)
    GET /api/applications/job/{job_id}/
    """
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployerOwner)
    
    def get_queryset(self):
        job_id = self.kwargs['job_id']
        employer = get_object_or_404(Employer, user=self.request.user)
        job = get_object_or_404(Job, id=job_id, employer=employer)
        return Application.objects.filter(job=job).select_related(
            'candidate', 'resume'
        )

class WithdrawApplicationView(APIView):
    """
    Withdraw an application (candidate only)
    POST /api/applications/{id}/withdraw/
    """
    permission_classes = (permissions.IsAuthenticated, IsCandidateOwner)
    
    def post(self, request, pk):
        candidate = get_object_or_404(Candidate, user=request.user)
        application = get_object_or_404(Application, id=pk, candidate=candidate)
        
        if application.status in ['hired', 'rejected']:
            return Response({
                'error': 'Cannot withdraw application with this status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'withdrawn'
        application.save()
        
        return Response({
            'message': 'Application withdrawn successfully'
        }, status=status.HTTP_200_OK)