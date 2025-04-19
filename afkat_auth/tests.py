
# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.test import APIClient
from rest_framework import status
import json


class AfkatAuthTests(TestCase):
    def setUp(self):
        # Create a test client
        self.client = APIClient()

        # Create a test user
        self.test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }

        # URLs
        self.register_url = reverse('rest_register')
        self.login_url = reverse('rest_login')
        self.user_details_url = reverse('rest_user_details')

    def test_user_registration(self):
        """Test user registration functionality"""
        # Registration request
        response = self.client.post(
            self.register_url,
            self.test_user,
            format = 'json'
        )

        # Check if registration was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username = 'testuser').exists())

        # Check response content
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        """Test user login functionality"""
        # Create a user first
        User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'StrongPassword123!'
        )

        # Login request
        login_data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(
            self.login_url,
            login_data,
            format = 'json'
        )

        # Check if login was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_details(self):
        """Test retrieving user details"""
        # Create and authenticate a user
        user = User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'StrongPassword123!'
        )
        self.client.force_authenticate(user = user)

        # Get user details
        response = self.client.get(self.user_details_url)

        # Check if request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_invalid_registration(self):
        """Test registration with invalid data"""
        # Test with mismatched passwords
        invalid_user = self.test_user.copy()
        invalid_user['confirm_password'] = 'DifferentPassword123!'

        response = self.client.post(
            self.register_url,
            invalid_user,
            format = 'json'
        )

        # Check that registration failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        # Create a user first
        User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'StrongPassword123!'
        )

        # Try login with wrong password
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(
            self.login_url,
            login_data,
            format = 'json'
        )

        # Check that login failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)