from django.urls import path
from .views import (
    PlatformStatsView,
    JobAnalyticsView,
    EmployerAnalyticsView,
    CandidateAnalyticsView,
    ApplicationAnalyticsView,
    ExportApplicationsView,
    ExportJobsView,
    ExportCandidatesView,
    ExportEmployersView,
    DashboardStatsView
)

urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Analytics
    path('platform-stats/', PlatformStatsView.as_view(), name='platform-stats'),
    path('job-analytics/', JobAnalyticsView.as_view(), name='job-analytics'),
    path('employer-analytics/', EmployerAnalyticsView.as_view(), name='employer-analytics'),
    path('candidate-analytics/', CandidateAnalyticsView.as_view(), name='candidate-analytics'),
    path('application-analytics/', ApplicationAnalyticsView.as_view(), name='application-analytics'),
    
    # Exports
    path('export-applications/', ExportApplicationsView.as_view(), name='export-applications'),
    path('export-jobs/', ExportJobsView.as_view(), name='export-jobs'),
    path('export-candidates/', ExportCandidatesView.as_view(), name='export-candidates'),
    path('export-employers/', ExportEmployersView.as_view(), name='export-employers'),
]