from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from employers.models import Employer
from candidates.models import Candidate, Resume
from jobs.models import Job, JobCategory
from .models import Application

User = get_user_model()

class ApplicationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create employer and job
        employer_user = User.objects.create_user(
            email='employer@test.com',
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        employer = Employer.objects.create(
            user=employer_user,
            company_name='Test Company',
            contact_email='contact@test.com'
        )
        category = JobCategory.objects.create(
            name='IT',
            slug='it'
        )
        self.job = Job.objects.create(
            employer=employer,
            title='Test Job',
            description='Test description',
            requirements='Test requirements',
            category=category,
            job_type='full-time',
            location='Remote',
            is_active=True
        )
        
        # Create candidate
        self.candidate_user = User.objects.create_user(
            email='candidate@test.com',
            username='candidate',
            password='testpass123',
            user_type='candidate'
        )
        self.candidate = Candidate.objects.create(
            user=self.candidate_user,
            first_name='John',
            last_name='Doe'
        )
        
        # Authenticate as candidate
        response = self.client.post('/api/auth/login/', {
            'email': 'candidate@test.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_apply_to_job(self):
        """Test applying to a job"""
        data = {
            'job': self.job.id,
            'cover_letter': 'I am interested in this position'
        }
        
        response = self.client.post('/api/applications/apply/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Application.objects.filter(
            job=self.job,
            candidate=self.candidate
        ).exists())
    
    def test_duplicate_application(self):
        """Test applying to same job twice"""
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter='First application'
        )
        
        data = {
            'job': self.job.id,
            'cover_letter': 'Second application'
        }
        
        response = self.client.post('/api/applications/apply/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)