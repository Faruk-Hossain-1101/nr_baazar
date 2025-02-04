from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from shop.models.customer import Customer, Coupon, CustomerCoupon

class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            phone="1234567890",
            address="123 Main Street"
        )

    def test_customer_creation(self):
        """Test if a customer is created successfully."""
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.phone, "1234567890")
        self.assertEqual(self.customer.address, "123 Main Street")

    def test_customer_str(self):
        """Test the string representation of the customer model."""
        self.assertEqual(str(self.customer), "John Doe")


class CouponModelTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="TESTCOUPON",
            discount_type="flat",
            discount_amount=500,
            max_discount=500,
            expiry_date=timezone.now() + timedelta(days=90)
        )

    def test_coupon_creation(self):
        """Test if a coupon is created successfully."""
        self.assertEqual(self.coupon.code, "TESTCOUPON")
        self.assertEqual(self.coupon.discount_type, "flat")
        self.assertEqual(self.coupon.discount_amount, 500)
        self.assertEqual(self.coupon.max_discount, 500)
        self.assertTrue(self.coupon.is_active)

    def test_coupon_expiry(self):
        """Test if the coupon expiry date is correctly set."""
        self.assertGreater(self.coupon.expiry_date, timezone.now())

    def test_coupon_str(self):
        """Test the string representation of the coupon model."""
        self.assertEqual(str(self.coupon), "TESTCOUPON")


class CustomerCouponModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Alice Smith",
            phone="9876543210",
            address="456 Elm Street"
        )

        self.coupon = Coupon.objects.create(
            code="DISCOUNT50",
            discount_type="percentage",
            discount_amount=50,
            max_discount=200,
            expiry_date=timezone.now() + timedelta(days=90)
        )

        self.customer_coupon = CustomerCoupon.objects.create(
            customer=self.customer,
            coupon=self.coupon,
            is_used=False
        )

    def test_customer_coupon_creation(self):
        """Test if a customer coupon is created successfully."""
        self.assertEqual(self.customer_coupon.customer, self.customer)
        self.assertEqual(self.customer_coupon.coupon, self.coupon)
        self.assertFalse(self.customer_coupon.is_used)

    def test_customer_coupon_str(self):
        """Test the string representation of the customer coupon model."""
        self.assertEqual(str(self.customer_coupon), "Alice Smith - DISCOUNT50")
