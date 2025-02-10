from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from shop.models.customer import Coupon, CustomerCoupon, Customer
from decimal import Decimal
from django.contrib.messages import get_messages


class CouponViewTests(TestCase):

    def setUp(self):
        # Create a user for authentication if needed
        self.user = Customer.objects.create(phone='9876543210', name='Jhon Doe')

        # Create a coupon for testing
        self.coupon = Coupon.objects.create(
            code="DISCOUNT10",
            discount_type="flat",
            discount_amount=10,
            max_discount=0,
            minium_order=100,
            expiry_date=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )

        self.coupon2 = Coupon.objects.create(
            code="DISCOUNT11",
            discount_type="percentage",
            discount_amount=10,
            max_discount=10,
            minium_order=100,
            expiry_date=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )

    def test_view_coupon(self):
        response = self.client.get(reverse('view_coupon'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DISCOUNT10")

    def test_add_coupon_valid(self):
        response = self.client.post(reverse('add_coupon'), {
            'code': 'NEWCOUPON',
            'discount_type': 'flat',
            'discount_amount': 15,
            'max_discount': 0,
            'minium_order': 50,
            'expiry_date': timezone.now() + timezone.timedelta(days=2),
            'is_active': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to 'view_coupon'
        self.assertRedirects(response, reverse('view_coupon'))
        self.assertTrue(Coupon.objects.filter(code="NEWCOUPON").exists())

    def test_add_coupon_invalid(self):
        response = self.client.post(reverse('add_coupon'), {
            'code': '',
            'discount_type': 'flat',
            'discount_amount': 10,
            'expiry_date': timezone.now() + timezone.timedelta(days=2),
        })
        self.assertEqual(response.status_code, 302)  # Should redirect back
        # Retrieve the messages added to the response
        messages = list(get_messages(response.wsgi_request))
        # Check if the error message is in the messages list
        self.assertTrue(any("Please fill in all required fields." in str(message) for message in messages))
    
    def test_add_coupon_max_min_value_null(self):
        response = self.client.post(reverse('add_coupon'), {
            'code': 'NEWCOUPON',
            'discount_type': 'flat',
            'discount_amount': 10,
            'max_discount': '',
            'minium_order': '',
            'expiry_date': timezone.now() + timezone.timedelta(days=2),
        })
        
        self.assertEqual(response.status_code, 302)  # Redirects to 'view_coupon'
        self.assertRedirects(response, reverse('view_coupon'))
        self.assertTrue(Coupon.objects.filter(code="NEWCOUPON").exists())

    def test_edit_coupon_view(self):
        url = reverse('edit_coupon', args=[self.coupon.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/coupon/edit_coupon.html')
        self.assertIn('coupon', response.context)

    def test_edit_coupon_valid(self):
        response = self.client.post(reverse('edit_coupon', args=[self.coupon.id]), {
            'code': 'DISCOUNT20',
            'discount_type': 'flat',
            'discount_amount': 20,
            'max_discount': 0,
            'minium_order': 150,
            'expiry_date': timezone.now() + timezone.timedelta(days=5),
            'is_active': 'on'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_coupon'))
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.code, 'DISCOUNT20')

    def test_edit_coupon_invalid(self):
        response = self.client.post(reverse('edit_coupon', args=[self.coupon.id]), {
            'code': '',
            'discount_type': 'flat',
            'discount_amount': 20,
            'max_discount': 0,
            'minium_order': 150,
            'expiry_date': timezone.now() + timezone.timedelta(days=5),
            'is_active': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect back
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please fill in all required fields." in str(message) for message in messages))

    def test_edit_coupon_max_min_value_null(self):
        response = self.client.post(reverse('edit_coupon', args=[self.coupon.id]), {
            'code': 'DISCOUNT20',
            'discount_type': 'flat',
            'discount_amount': 20,
            'max_discount': '',
            'minium_order': '',
            'expiry_date': timezone.now() + timezone.timedelta(days=5),
            'is_active': 'on'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirects to 'view_coupon'
        self.assertRedirects(response, reverse('view_coupon'))
        self.assertTrue(Coupon.objects.filter(code="DISCOUNT20").exists())

    def test_apply_coupon_valid(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'DISCOUNT10',
            'total_amount': 200
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "₹ 10.00 Coupon applied!")
        self.assertEqual(response_data["final_amount"], "190.00")

    def test_apply_coupon_valid_with_percentage(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'DISCOUNT11',
            'total_amount': 200,
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "₹ 10.00 Coupon applied!")
        self.assertEqual(response_data["final_amount"], "190.00")

    def test_apply_coupon_invalid_code(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'INVALIDCOUPON',
            'total_amount': 200
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "Invalid or inactive coupon")

    def test_apply_coupon_blank_code(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': '',
            'total_amount': 200
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "Invalid input")

    def test_apply_coupon_expired(self):
        expired_coupon = Coupon.objects.create(
            code="EXPIREDCOUPON",
            discount_type="flat",
            discount_amount=5,
            max_discount=0,
            minium_order=50,
            expiry_date=timezone.now() - timezone.timedelta(days=1),
            is_active=True
        )
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'EXPIREDCOUPON',
            'total_amount': 100
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "Coupon has expired")

    def test_apply_coupon_minimum_order(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'DISCOUNT10',
            'total_amount': 50
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "Order price should be higher than ₹100.00")

    def test_apply_coupon_already_used(self):
        CustomerCoupon.objects.create(
            coupon=self.coupon,
            customer=self.user,
            is_used=True
        )
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'DISCOUNT10',
            'total_amount': 200
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "Coupon already used by")

    def test_apply_coupon_invalid_total_amount(self):
        response = self.client.post(reverse('apply_coupon'), {
            'coupon': 'DISCOUNT10',
            'total_amount': 'xyz'
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Invalid total amount")
    
    def test_apply_coupon_invalid_method(self):
        response = self.client.get(reverse('apply_coupon'))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Invalid request method")


