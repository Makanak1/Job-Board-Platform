from django.urls import path
from .views import (
    CandidateListView,
    CandidateDetailView,
    CandidateProfileView,
    ResumeUploadView,
    ResumeListView,
    ResumeDetailView,
    CandidateApplicationsView,
    CandidateStatsView
)

urlpatterns = [
    path('', CandidateListView.as_view(), name='candidate-list'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('profile/', CandidateProfileView.as_view(), name='candidate-profile'),
    path('resumes/', ResumeListView.as_view(), name='resume-list'),
    path('resumes/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/<int:pk>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('applications/', CandidateApplicationsView.as_view(), name='candidate-applications'),
    path('stats/', CandidateStatsView.as_view(), name='candidate-stats'),
]