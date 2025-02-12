from django.test import TestCase
from django.utils.timezone import now
from unittest.mock import patch
from shop.models.order import Order
from shop.models.customer import Customer, Coupon, CustomerCoupon
from datetime import timedelta
from django.utils import timezone
import uuid


class OrderSignalTestCase(TestCase):

    @patch('shop.signals.requests.post')  # Mock the external API call
    def test_after_order_create_coupon_created(self, mock_post):
        # Create a customer
        customer = Customer.objects.create(name="John Doe", phone="1234567890")
        
        # Create an order with total_amount >= 2000
        order = Order.objects.create(
            customer=customer,
            order_number="ORD67890",
            total_amount=2000.00,
            discount_amount=200.00,
            actual_amount=1800.00,
        )

        # Check if a coupon is created for the customer
        customer_coupon = CustomerCoupon.objects.filter(customer=customer).first()
        self.assertIsNotNone(customer_coupon)  # Make sure the coupon is created
        self.assertEqual(customer_coupon.is_used, False)  # Ensure coupon is not used
        
        coupon = customer_coupon.coupon
        self.assertEqual(coupon.discount_amount, 10)  # Ensure correct discount
        self.assertEqual(coupon.max_discount, 500)  # Ensure max discount is correct
        self.assertEqual(coupon.minium_order, 2000)  # Ensure minimum order amount is correct
        self.assertTrue(coupon.is_active)  # Ensure coupon is active
        self.assertEqual(coupon.code[:6], f"SAVE10")  # Ensure the coupon code starts with 'SAVE10'

        # Verify that the mock POST request was made (WhatsApp API)
        self.assertTrue(mock_post.called)
        # Check that the correct data was passed in the mock request
        self.assertIn('whatsapp', mock_post.call_args[1]['json']['messaging_product'])
        self.assertIn('after_order', mock_post.call_args[1]['json']['template']['name'])

    @patch('shop.signals.requests.post')  # Mock the external API call
    def test_after_order_create_no_coupon_for_small_order(self, mock_post):
        # Create a customer
        customer = Customer.objects.create(name="Jane Doe", phone="0987654321")

        # Create an order with total_amount < 2000 (no coupon should be created)
        order = Order.objects.create(
            customer=customer,
            order_number="ORD12346",
            total_amount=1500,  # This does NOT qualify for a coupon
            discount_amount=100,
            actual_amount=1400,
        )

        # Check if no coupon is created for the customer
        customer_coupon = CustomerCoupon.objects.filter(customer=customer).first()
        self.assertIsNone(customer_coupon)  # No coupon should be created

        # Verify that no WhatsApp message is sent
        self.assertFalse(mock_post.called)

    @patch('shop.signals.requests.post')  # Mock the external API call
    def test_after_order_create_coupon_updated(self, mock_post):
        # Create a customer and a coupon for them
        customer = Customer.objects.create(name="Mike Doe", phone="1122334455")
        coupon = Coupon.objects.create(
            code="SAVE10-ABC123", discount_type="percentage", discount_amount=10,
            max_discount=500, minium_order=2000, coupon_type="individual", expiry_date=now() + timedelta(days=90)
        )
        customer_coupon = CustomerCoupon.objects.create(customer=customer, coupon=coupon, is_used=False)

        # Create an order with total_amount >= 2000 (this should update the coupon)
        order = Order.objects.create(
            customer=customer,
            order_number="ORD12347",
            total_amount=3000,  # This qualifies for a coupon
            discount_amount=100,
            actual_amount=2900
        )

        # Check if the existing coupon was updated
        customer_coupon.refresh_from_db()
        self.assertFalse(customer_coupon.is_used)  # Ensure the coupon is still not used
        self.assertTrue(customer_coupon.coupon.is_active)  # Ensure coupon is active
        self.assertEqual(customer_coupon.coupon.code[:6], "SAVE10")  # Ensure coupon code starts with 'SAVE10'

        # Verify that the mock POST request was made (WhatsApp API)
        self.assertTrue(mock_post.called)

    @patch('shop.signals.requests.post')  # Mock the external API call
    def test_after_order_create_coupon_used(self, mock_post):
        # Create a customer and an order with a coupon
        customer = Customer.objects.create(name="Sara Doe", phone="5566778899")
        coupon = Coupon.objects.create(
            code="SAVE10-XYZ987", discount_type="percentage", discount_amount=10,
            max_discount=500, minium_order=2000, coupon_type="individual", expiry_date=now() + timedelta(days=90)
        )
        customer_coupon = CustomerCoupon.objects.create(customer=customer, coupon=coupon, is_used=True)

        # Create an order that uses this coupon
        order = Order.objects.create(
            customer=customer,
            order_number="ORD12348",
            total_amount=3500,  # This qualifies for the coupon
            actual_amount=3500,
            discount_amount=0,
            coupon=coupon  # Associating the coupon with the order
        )

        # Ensure the coupon is marked as used and inactive
        customer_coupon.refresh_from_db()
        self.assertFalse(customer_coupon.is_used)  # Ensure coupon is marked as used
        self.assertTrue(customer_coupon.coupon.is_active)  # Ensure coupon is inactive

        # Verify that the mock POST request was made (WhatsApp API)
        self.assertTrue(mock_post.called)
