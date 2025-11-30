from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class ReportsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            username='admin',
            password='adminpass123',
            user_type='admin'
        )
        
        # Login
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'adminpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_platform_stats(self):
        """Test platform statistics endpoint"""
        response = self.client.get('/api/reports/platform-stats/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.data)
        self.assertIn('jobs', response.data)
        self.assertIn('applications', response.data)