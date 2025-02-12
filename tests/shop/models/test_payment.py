from django.test import TestCase
from django.utils import timezone
from shop.models.payment import Payment
from shop.models.order import Order
from shop.models.customer import Customer

class PaymentModelTest(TestCase):
    def setUp(self):
        """Setup test data for Payment model"""
        self.customer = Customer.objects.create(
            name="John Doe",
            phone="1234567890",
            address="123 Main Street"
        )

        self.order = Order.objects.create(
            order_number="ORD1001",
            customer=self.customer,
            total_amount=1500.00,
            discount_amount=200.00,
            actual_amount=1300.00,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            payment_method="online",
            payment_status="success",
            paid_amount=1300.00,
            due_amount=0.00
        )

    def test_payment_creation(self):
        """Test if a payment is created successfully."""
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.payment_method, "online")
        self.assertEqual(self.payment.payment_status, "success")
        self.assertEqual(self.payment.paid_amount, 1300.00)
        self.assertEqual(self.payment.due_amount, 0.00)

    def test_payment_transaction_id(self):
        """Test if transaction_id is auto-generated."""
        self.assertIsNotNone(self.payment.transaction_id)

    def test_payment_str(self):
        """Test the string representation of the payment model."""
        self.assertEqual(str(self.payment), f"Payment {self.payment.id} for Order {self.order.id}")

    def test_payment_date_auto_now_add(self):
        """Test if payment_date is automatically set."""
        self.assertIsNotNone(self.payment.payment_date)
        self.assertLessEqual(self.payment.payment_date, timezone.now())
