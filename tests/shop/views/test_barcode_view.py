from django.test import TestCase, Client
from django.urls import reverse
from shop.models.product import Product
from unittest.mock import patch

class PrintBarcodeViewTests(TestCase):
    
    def setUp(self):
        # Create sample products
        self.product1 = Product.objects.create(
            name="Product 1",
            sku="SKU001",
            stock_quantity=3,  # Odd quantity
            purchase_price=100.00,
            actual_price=120.00,
            selling_price=130.00,
            discount_type="flat",
            discount_amount=5.00,
            description="Test product 1",
            color="Red",
            size="M",
            cell="A1",
            barcode="SKU00100000"
        )
        
        self.product2 = Product.objects.create(
            name="Product 2",
            sku="SKU002",
            stock_quantity=5,  # odd quantity
            purchase_price=50.00,
            actual_price=60.00,
            selling_price=70.00,
            discount_type="flat",
            discount_amount=2.00,
            description="Test product 2",
            color="Blue",
            size="L",
            cell="B1",
            barcode="SKU00200000"
        )

        self.product3 = Product.objects.create(
            name="Product 3",
            sku="SKU003",
            stock_quantity=2,  # Even quantity
            purchase_price=50.00,
            actual_price=60.00,
            selling_price=70.00,
            discount_type="flat",
            discount_amount=20.00,
            description="Test product 3",
            color="Blue",
            size="L",
            cell="B1",
            barcode="SKU00200000"
        )

        # Create a client for testing
        self.client = Client()

    @patch('shop.views.product.Product.objects.filter')  # Mock the database call
    def test_print_labels(self, mock_filter):
        # Mock the return value for the filtered products
        mock_filter.return_value = [self.product1, self.product2]
        
        # Simulate a GET request with product IDs
        response = self.client.get(reverse('preview_barcode') + "?products=" + str(self.product1.id) + "," + str(self.product2.id))
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Get the label pairs from the context
        label_pairs = response.context['label_pairs']
        
        # Validate the label pairs
        # Product 1 has 3 units, so it should generate 1 full pair and 1 single label.
        # Product 2 has 4 units, so it should generate 2 full pairs.
        
        expected_label_pairs = [
            ('SKU001', 'SKU001'),  # First full pair for Product 1
            ('SKU002', 'SKU002'),  # First pair for Product 2
            ('SKU002', 'SKU002'),   # Second pair for Product 2
            ('SKU001', 'SKU002')     
        ]
        
        self.assertEqual(label_pairs, expected_label_pairs)

    # Reminder will be there
    @patch('shop.views.product.Product.objects.filter')  # Mock the database call
    def test_print_odd_labels(self, mock_filter):
        # Mock the return value for the filtered products
        mock_filter.return_value = [self.product1, self.product3]
        
        # Simulate a GET request with product IDs
        response = self.client.get(reverse('preview_barcode') + "?products=" + str(self.product1.id) + "," + str(self.product2.id))
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Get the label pairs from the context
        label_pairs = response.context['label_pairs']
        
        # Validate the label pairs
        # Product 1 has 3 units, so it should generate 1 full pair and 1 single label.
        # Product 2 has 4 units, so it should generate 2 full pairs.
        
        expected_label_pairs = [
            ('SKU001', 'SKU001'),  # First full pair for Product 1
            ('SKU003', 'SKU003'),  # First pair for Product 3
            ('SKU001', None)      # Single label for Product 1 (due to odd stock_quantity)
        ]
        
        self.assertEqual(label_pairs, expected_label_pairs)

    def test_show_barcode_data(self):
        response = self.client.get(reverse('show_barcode_data'))
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/barcode/index.html')
        self.assertIn('products', response.context)

    def test_preview_barcode(self):
        # Simulate a GET request with no products
        response = self.client.get(reverse('preview_barcode') + "?products=1,2")
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Get the label pairs from the context
        label_pairs = response.context['label_pairs']
        
        # Expecting an empty list since no products were selected
        self.assertEqual(label_pairs, [])

    def test_print_barcode(self):
        
        response = self.client.get(reverse('print_barcode'), {'p_ids': f"{self.product1.id}, {self.product2.id}"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        
        self.assertTrue(self.product1.is_printed)
        self.assertTrue(self.product2.is_printed)

