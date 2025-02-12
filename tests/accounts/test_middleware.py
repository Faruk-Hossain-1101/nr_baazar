from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import redirect
from django.http import HttpResponse
from unittest.mock import MagicMock
from accounts.middleware import role_required  

# Dummy view to test the decorator
def dummy_view(request):
    return HttpResponse("Success")

class RoleRequiredDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_with_role = User(username='testuser')
        self.user_with_role.role = 'admin'  # Assuming role is dynamically assigned
        self.user_without_role = User(username='testuser2')
        self.user_without_role.role = 'user'
        self.anonymous_user = AnonymousUser()

    def test_redirects_anonymous_user_to_login(self):
        request = self.factory.get('/')
        request.user = self.anonymous_user
        decorated_view = role_required(['admin'])(dummy_view)
        response = decorated_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_allows_user_with_required_role(self):
        request = self.factory.get('/')
        request.user = self.user_with_role
        decorated_view = role_required(['admin'])(dummy_view)
        response = decorated_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Success")

    def test_redirects_user_without_required_role(self):
        request = self.factory.get('/')
        request.user = self.user_without_role
        decorated_view = role_required(['admin'])(dummy_view)
        response = decorated_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/sell/')
