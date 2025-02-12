from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from django.contrib import messages

class AuthenticationViewsTestCase(TestCase):

    def setUp(self):
        # Create a test user for authentication
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword', email="test@gmail.com")

    def test_login_view_valid_credentials(self):
        # Test login with valid credentials
        response = self.client.post(reverse('login_view'), {'username': 'testuser', 'password': 'testpassword'})
        
        # Check if the response redirects to the home page
        self.assertEqual(response.url, reverse('home')) 
        # Check if the user is logged in
        self.assertEqual(str(self.client.session['_auth_user_id']), str(self.user.pk))

    def test_login_view_invalid_credentials(self):
        # Test login with invalid credentials
        response = self.client.post(reverse('login_view'), {'username': 'testuser', 'password': 'wrongpassword'})
        
        # Check if the response renders the login page with error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')
    
    def test_logout_view(self):
        # Log in the user before testing logout
        self.client.login(username='testuser', password='testpassword')
        
        # Test logout
        response = self.client.get(reverse('logout_view'))
        
        # Check if the response redirects to the login page
        self.assertRedirects(response, reverse('login_view'))
        # Check if the user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)