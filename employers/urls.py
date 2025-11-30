from django.urls import path
from .views import (
    EmployerListView,
    EmployerDetailView,
    EmployerProfileView,
    EmployerJobsView,
    EmployerStatsView
)

urlpatterns = [
    path('', EmployerListView.as_view(), name='employer-list'),
    path('<int:pk>/', EmployerDetailView.as_view(), name='employer-detail'),
    path('profile/', EmployerProfileView.as_view(), name='employer-profile'),
    path('my-jobs/', EmployerJobsView.as_view(), name='employer-jobs'),
    path('stats/', EmployerStatsView.as_view(), name='employer-stats'),
]