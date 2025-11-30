from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from employers.models import Employer
from candidates.models import Candidate

User = get_user_model()

class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
    
    def test_register_employer(self):
        """Test employer registration"""
        data = {
            'email': 'employer@test.com',
            'username': 'testemployer',
            'password': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'employer',
            'phone': '+1234567890',
            'employer_profile': {
                'company_name': 'Test Company',
                'contact_email': 'contact@test.com',
                'location': 'New York'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='employer@test.com').exists())
        self.assertTrue(Employer.objects.filter(company_name='Test Company').exists())
    
    def test_register_candidate(self):
        """Test candidate registration"""
        data = {
            'email': 'candidate@test.com',
            'username': 'testcandidate',
            'password': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'candidate',
            'phone': '+1234567890',
            'candidate_profile': {
                'first_name': 'John',
                'last_name': 'Doe',
                'location': 'Los Angeles'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='candidate@test.com').exists())
        self.assertTrue(Candidate.objects.filter(first_name='John').exists())
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'differentpass',
            'user_type': 'candidate'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='testpass123',
            user_type='candidate'
        )
    
    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)