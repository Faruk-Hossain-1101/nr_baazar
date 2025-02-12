from django.test import TestCase
from django.utils import timezone
from shop.models.order import Order, OrderItem
from shop.models.customer import Customer, Coupon

class OrderModelTest(TestCase):
    def setUp(self):
        """Setup test data for Order model"""
        self.customer = Customer.objects.create(
            name="John Doe",
            phone="1234567890",
            address="123 Main Street"
        )

        self.coupon = Coupon.objects.create(
            code="SAVE10",
            discount_type="percentage",
            discount_amount=10,
            max_discount=100,
            expiry_date=timezone.now() + timezone.timedelta(days=90)
        )

        self.order = Order.objects.create(
            order_number="ORD12345",
            customer=self.customer,
            total_amount=1000.00,
            discount_amount=100.00,
            actual_amount=900.00,
            coupon=self.coupon
        )

    def test_order_creation(self):
        """Test if an order is created successfully."""
        self.assertEqual(self.order.order_number, "ORD12345")
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.total_amount, 1000.00)
        self.assertEqual(self.order.discount_amount, 100.00)
        self.assertEqual(self.order.actual_amount, 900.00)
        self.assertEqual(self.order.coupon, self.coupon)

    def test_order_str(self):
        """Test the string representation of the order model."""
        self.assertEqual(str(self.order), f"Order ORD12345 by {self.customer.name}")

    def test_order_has_timestamp(self):
        """Test if order has auto-populated timestamps."""
        self.assertIsNotNone(self.order.order_date)


class OrderItemModelTest(TestCase):
    def setUp(self):
        """Setup test data for OrderItem model"""
        self.customer = Customer.objects.create(
            name="Jane Doe",
            phone="9876543210",
            address="456 Elm Street"
        )

        self.order = Order.objects.create(
            order_number="ORD67890",
            customer=self.customer,
            total_amount=2000.00,
            discount_amount=200.00,
            actual_amount=1800.00,
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_name="T-Shirt",
            actual_price=500.00,
            discount_amount=50.00,
            color="Blue",
            size="L",
            quantity=2,
            sku="TSH456"
        )

    def test_order_item_creation(self):
        """Test if an order item is created successfully."""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product_name, "T-Shirt")
        self.assertEqual(self.order_item.actual_price, 500.00)
        self.assertEqual(self.order_item.discount_amount, 50.00)
        self.assertEqual(self.order_item.color, "Blue")
        self.assertEqual(self.order_item.size, "L")
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.sku, "TSH456")

    def test_order_item_str(self):
        """Test the string representation of the order item model."""
        self.assertEqual(str(self.order_item), "T-Shirt - 2")

    def test_order_item_has_timestamps(self):
        """Test if order item has auto-populated timestamps."""
        self.assertIsNotNone(self.order_item.created_at)
        self.assertIsNotNone(self.order_item.updated_at)
