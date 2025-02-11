from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser

class IndexViewTests(TestCase):

    def setUp(self):
        # Create a client for testing
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="testuser", password="password123", email="test@gmail.com", role="manager")
        self.client.force_login(self.user)

    def test_index_view(self):
        """ Test if the index view renders correctly """
        response = self.client.get(reverse('home'))  # Ensure 'index' matches the URL name in urls.py
        self.assertEqual(response.status_code, 200)  # Check if the response is 200 OK
        self.assertTemplateUsed(response, 'shop/index.html')  # Check if the correct template is used
