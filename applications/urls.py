from django.urls import path
from .views import (
    ApplicationCreateView,
    ApplicationDetailView,
    ApplicationUpdateStatusView,
    CandidateApplicationListView,
    EmployerApplicationListView,
    JobApplicationsView,
    WithdrawApplicationView
)

urlpatterns = [
    path('apply/', ApplicationCreateView.as_view(), name='application-create'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('<int:pk>/update-status/', ApplicationUpdateStatusView.as_view(), name='application-update-status'),
    path('<int:pk>/withdraw/', WithdrawApplicationView.as_view(), name='application-withdraw'),
    path('my-applications/', CandidateApplicationListView.as_view(), name='candidate-applications'),
    path('received/', EmployerApplicationListView.as_view(), name='employer-applications'),
    path('job/<int:job_id>/', JobApplicationsView.as_view(), name='job-applications'),
]