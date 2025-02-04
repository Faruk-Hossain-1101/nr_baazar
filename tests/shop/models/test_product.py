from django.test import TestCase
from shop.models.product import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="T-Shirt",
            purchase_price=500.00,
            actual_price=1000.00,
            discount_type="percentage",
            discount_amount=20.00,
            color="Red",
            size="M",
            stock_quantity=50,
            barcode="1234567890123",
            sku="TSH123",
            description="A comfortable cotton T-shirt"
        )

    def test_product_creation(self):
        """Test if a product is created successfully."""
        self.assertEqual(self.product.name, "T-Shirt")
        self.assertEqual(self.product.purchase_price, 500.00)
        self.assertEqual(self.product.actual_price, 1000.00)
        self.assertEqual(self.product.discount_type, "percentage")
        self.assertEqual(self.product.discount_amount, 20.00)
        self.assertEqual(self.product.color, "Red")
        self.assertEqual(self.product.size, "M")
        self.assertEqual(self.product.stock_quantity, 50)
        self.assertEqual(self.product.barcode, "1234567890123")
        self.assertEqual(self.product.sku, "TSH123")
        self.assertEqual(self.product.description, "A comfortable cotton T-shirt")

    def test_product_str(self):
        """Test the string representation of the product model."""
        self.assertEqual(str(self.product), "T-Shirt")

    def test_discount_null_values(self):
        """Test if discount fields accept null values when discount is not provided."""
        product_no_discount = Product.objects.create(
            name="Jeans",
            purchase_price=700.00,
            actual_price=1400.00,
            stock_quantity=30,
            sku="JNS456"
        )
        self.assertIsNone(product_no_discount.discount_type)
        self.assertIsNone(product_no_discount.discount_amount)

    def test_auto_timestamps(self):
        """Test if the created_at and updated_at fields are auto-populated."""
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)
