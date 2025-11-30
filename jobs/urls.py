from django.urls import path
from .advanced_search import AdvancedJobSearchView
from .views import (
    JobCategoryListView,
    JobListView,
    JobDetailView,
    JobCreateView,
    JobUpdateView,
    JobDeleteView,
    JobToggleActiveView,
    JobSearchView
)

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('categories/', JobCategoryListView.as_view(), name='job-categories'),
    path('search/', JobSearchView.as_view(), name='job-search'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('<slug:slug>/', JobDetailView.as_view(), name='job-detail'),
    path('<slug:slug>/update/', JobUpdateView.as_view(), name='job-update'),
    path('<slug:slug>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('<slug:slug>/toggle-active/', JobToggleActiveView.as_view(), name='job-toggle-active'),
    path('advanced-search/', AdvancedJobSearchView.as_view(), name='advanced-job-search'),
]