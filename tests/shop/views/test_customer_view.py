from django.test import TestCase, Client
from django.urls import reverse
from shop.models.customer import Customer

class GetCustomerByPhoneTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a sample customer in the database
        self.customer = Customer.objects.create(
            name="John Doe",
            phone="1234567890",
            address="123 Main Street"
        )

    def test_get_customer_by_valid_phone(self):
        """ Test API returns correct customer data when phone number exists """
        response = self.client.get(reverse('get_customer_by_phone'), {'phone': '1234567890'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': True,
            'name': "John Doe",
            'address': "123 Main Street"
        })

    def test_get_customer_by_invalid_phone(self):
        """ Test API returns success: False when phone number does not exist """
        response = self.client.get(reverse('get_customer_by_phone'), {'phone': '9999999999'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False})

    def test_get_customer_without_phone_param(self):
        """ Test API returns success: False when no phone number is provided """
        response = self.client.get(reverse('get_customer_by_phone'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False})
