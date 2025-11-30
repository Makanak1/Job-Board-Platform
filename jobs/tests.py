from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from employers.models import Employer
from .models import Job, JobCategory

User = get_user_model()

class JobTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create employer user
        self.employer_user = User.objects.create_user(
            email='employer@test.com',
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name='Test Company',
            contact_email='contact@test.com'
        )
        
        # Create category
        self.category = JobCategory.objects.create(
            name='Software Development',
            slug='software-development'
        )
        
        # Authenticate
        response = self.client.post('/api/auth/login/', {
            'email': 'employer@test.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_job(self):
        """Test job creation"""
        data = {
            'title': 'Senior Python Developer',
            'description': 'We are looking for a senior Python developer',
            'requirements': '5+ years of Python experience',
            'category': self.category.id,
            'job_type': 'full-time',
            'experience_level': 'senior',
            'location': 'Remote',
            'salary_min': 80000,
            'salary_max': 120000,
            'is_active': True
        }
        
        response = self.client.post('/api/jobs/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Job.objects.filter(title='Senior Python Developer').exists())
    
    def test_list_jobs(self):
        """Test listing jobs"""
        Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test description',
            requirements='Test requirements',
            category=self.category,
            job_type='full-time',
            location='New York',
            is_active=True
        )
        
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('applications_count', response.data['results'][0])
    
    def test_job_search(self):
        """Test job search"""
        Job.objects.create(
            employer=self.employer,
            title='Python Developer',
            description='Python job',
            requirements='Python skills',
            category=self.category,
            job_type='full-time',
            location='San Francisco',
            is_active=True
        )
        
        response = self.client.get('/api/jobs/search/?keyword=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)