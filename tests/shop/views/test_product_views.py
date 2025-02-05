from django.test import TestCase, Client
from django.urls import reverse
from shop.models.product import Product
from decimal import Decimal
import pytest # type: ignore
from unittest.mock import patch
from django.contrib.messages import get_messages

class ProductViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Test Product",
            sku="TP123",
            stock_quantity=10,
            purchase_price=Decimal('100.00'),
            actual_price=Decimal('120.00'),
            selling_price=Decimal('130.00'),
            discount_type="Percentage",
            discount_amount=Decimal('10.00'),
            description="Test Description",
            color="Red",
            size="M",
            cell="A1",
            barcode="TP12300000"
        )

    def test_add_product_success(self):
        response = self.client.post(reverse('add_product'), {
            'name': 'New Product',
            'stock_quantity': 5,
            'purchase_price': '50.00',
            'actual_price': '60.00',
            'selling_price': '70.00',
            'discount_type': 'flat',
            'discount_amount': '5.00',
            'description': 'A new test product',
            'color': 'Blue',
            'size': 'L',
            'cell': 'B2'
        })
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertTrue(Product.objects.filter(name="New Product").exists())

    def test_stock_quentity_not_digit(self):
        response = self.client.post(reverse('add_product'), {
            'name': 'New Product 2',  # Missing name
            'stock_quantity': "",
            'purchase_price': '50.00',
            'actual_price': '60.00',
            'selling_price': '70.00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock quantity must be a valid number.")

    def test_price_none(self):
        response = self.client.post(reverse('add_product'), {
            'name': 'New Product 2',  # Missing name
            'stock_quantity': 5,
            'purchase_price': '',
            'actual_price': '',
            'selling_price': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Purchase price is required.")
        self.assertContains(response, "Actual price is required.")
        self.assertContains(response, "Selling price is required.")


    def test_invalide_decimale_fornat(self):
        response = self.client.post(reverse('add_product'), {
            'name': 'New Product 2',  # Missing name
            'stock_quantity': 5,
            'purchase_price': 'abc',
            'actual_price': '60.00',
            'selling_price': '70.00',
            'discount_amount': 'xyz'
        })
        assert "Invalid decimal format in price fields." in response.content.decode()
        assert "None" in response.content.decode()
        assert response.status_code == 200
    


    def test_add_product_missing_required_fields(self):
        response = self.client.post(reverse('add_product'), {
            'name': '',  # Missing name
            'stock_quantity': 5,
            'purchase_price': '50.00',
            'actual_price': '60.00',
            'selling_price': '70.00',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product name is required.")


    def test_view_product_list(self):
        response = self.client.get(reverse('view_product'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")

    def test_edit_product_success(self):
        response = self.client.post(reverse('edit_product', args=[self.product.id]), {
            'name': 'Updated Product',
            'sku': 'TP123',
            'stock_quantity': 15,
            'purchase_price': '110.00',
            'actual_price': '130.00',
            'selling_price': '140.00',
            'discount_type': 'Flat',
            'discount_amount': '15.00',
            'description': 'Updated description',
            'color': 'Green',
            'size': 'XL',
            'cell': 'C3',
            'barcode': 'TP12300000'
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.stock_quantity, 15)

    def test_edit_product_invalid(self):
        response = self.client.post(reverse('edit_product', args=[self.product.id]), {
            'name': '',  # Empty name should trigger validation error
            'sku': 'TP123',
            'stock_quantity': '',
            'purchase_price': '',
            'actual_price': '',
            'selling_price': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock quantity must be a valid number.")
        self.assertContains(response, "Purchase price is required.")
        self.assertContains(response, "Actual price is required.")
        self.assertContains(response, "Selling price is required.")


    # def test_sku_uniqueness(self):
    #     product_data = {
    #         'name': 'Test Product with Duplicate SKU',
    #         'stock_quantity': 5,
    #         'purchase_price': '50.00',
    #         'actual_price': '60.00',
    #         'selling_price': '70.00',
    #         'discount_type': 'flat',
    #         'discount_amount': '5.00',
    #         'description': 'A test product to check SKU uniqueness',
    #         'color': 'Blue',
    #         'size': 'M',
    #         'cell': 'B2'
    #     }

    #     # Mock the `generate_sku` function to always return the same SKU
    #     with patch('shop.views.product.generate_sku', return_value='TEST123'):
    #         # Create the first product (with the mocked SKU)
    #         response = self.client.post(reverse('add_product'), data=product_data)
    #         self.assertEqual(response.status_code, 302)  # Assuming the redirect occurs after success

    #         # Create another product with the same SKU (to test uniqueness)
    #         response = self.client.post(reverse('add_product'), data=product_data)

    #         # Assert that the IntegrityError message is triggered for the second product
    #         messages = list(get_messages(response.wsgi_request))
    #         self.assertEqual(str(messages[1]), "SKU must be unique.")

    #         # Check if the second product was not added (SKU should be unique)
    #         self.assertEqual(Product.objects.filter(sku='TEST123').count(), 1)