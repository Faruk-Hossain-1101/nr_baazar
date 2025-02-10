from django.test import TestCase, Client
from django.urls import reverse
from shop.models.product import Product
from shop.models.customer import Coupon, Customer, CustomerCoupon
from shop.models.order import Order, OrderItem
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
import json
from shop.views.sell import custom_serializer


class ShopViewTests(TestCase):
    def setUp(self):
        """Setup test data for all test cases"""
        self.client = Client()
        
        # Create a sample product
        self.product = Product.objects.create(
            name="Test Product",
            purchase_price=Decimal("50.00"),
            actual_price=Decimal("100.00"),
            discount_type="flat",
            discount_amount=Decimal("10.00"),
            selling_price=Decimal("90.00"),
            stock_quantity=10,
            barcode="1234567890",
            sku="TEST123"
        )

        # Create a test customer
        self.customer = Customer.objects.create(
            name="John Doe",
            phone="1234567890",
            address="123 Street, City"
        )

        # Create a test coupon
        self.coupon = Coupon.objects.create(
            code="DISCOUNT10",
            discount_type="flat",
            discount_amount=10,
            max_discount=0,
            minium_order=100,
            expiry_date=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
            coupon_type="individual"
        )

    def test_get_product_details_valid(self):
        """Test getting product details with a valid barcode"""
        response = self.client.get(reverse('get_product_details'), {'barcode': '1234567890'})
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "success": True,
            "product_name": "Test Product",
            "rate": "100.00",  # Convert Decimal to str
            "discount": "10.00",  # Convert Decimal to str
            "color": None,
            "size": None,
            "sku": "TEST123",
        }
        self.assertJSONEqual(response.content, expected_data)

    def test_get_product_details_invalid_barcode(self):
        """Test getting product details with an invalid barcode"""
        response = self.client.get(reverse('get_product_details'), {'barcode': '0000000000'})
        self.assertEqual(response.status_code, 404)

    def test_check_discount_valid(self):
        """Test discount calculation with a valid discount"""
        response = self.client.get(reverse('check_discount'), {'barcode': '1234567890', 'discount_amount': '5'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Valid discount'})

    def test_check_discount_invalid_discount(self):
        """Test when discount is too high and goes below margin"""
        response = self.client.get(reverse('check_discount'), {'barcode': '1234567890', 'discount_amount': '95'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Discount too high! Minimum 5% margin required.'})

    def test_check_qty_valid(self):
        """Test if stock is available"""
        response = self.client.get(reverse('check_qty'), {'barcode': '1234567890', 'qty': '5'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Product available!'})

    def test_check_qty_insufficient_stock(self):
        """Test when requested quantity exceeds available stock"""
        response = self.client.get(reverse('check_qty'), {'barcode': '1234567890', 'qty': '20'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Quantity higher than stock availability!'})

    def test_show_invoice_get(self):
        """Test invoice calculation and rendering"""
        session = self.client.session
        session['cart'] = {
            "items": [
                {"sku": "TEST123", "rate": "100.00", "qty": "2", "discount": "10.00"}
            ],
            "paidAmount": "180.00",
            "coupon": {"code": "DISCOUNT50", "amount": "50.00"},
            "roundOff": "0.00"
        }
        session.save()

        response = self.client.get(reverse('show_invoice'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/sell/invoice.html")
        self.assertIn("invoice_no", response.context)

    def test_show_invoice_post(self):
        """Test storing cart data in session via POST"""
        response = self.client.post(reverse('show_invoice'), json.dumps({
            "cart": {
                "items": [
                    {"sku": "TEST123", "rate": "100.00", "qty": "2", "discount": "10.00"}
                ],
                "paidAmount": "180.00",
                "coupon": {"code": "DISCOUNT50", "amount": "50.00"},
                "roundOff": "0.00"
            }
        }), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'cart': {
            "items": [
                {"sku": "TEST123", "rate": "100.00", "qty": "2", "discount": "10.00"}
            ],
            "paidAmount": "180.00",
            "coupon": {"code": "DISCOUNT50", "amount": "50.00"},
            "roundOff": "0.00"
        }})

    def test_after_bill_print(self):
        """Test order creation after bill print"""
        # Get the current UTC time and adjust for Kolkata timezone (UTC+5:30)
        current_time_utc = datetime.utcnow()
        kolkata_time = current_time_utc + timedelta(hours=5, minutes=30)
        formatted_date = kolkata_time.strftime('%d/%m/%Y')

        session = self.client.session
        cart ={
            "items": [
                {"sku": "TEST123", "rate": "100.00", "qty": "2", "discount": "10.00"}
            ],
            "customer": {
                "name": "John Doe",
                "phone": "1234567890",
                "address": "123 Street, City"
            },
            "coupon": {
                "code": "DISCOUNT10",
                "amount": "50.00"
            },
            "paymentType": "cash",
            "paidAmount": "180.00",
            "roundOff": "0.00"
        }
        context = {
            "cart_data": cart,
            'actual_price': '200.00',
            "item_discount": '20.00',
            "total_amount": '180.00',
            "grand_total": '180.00',
            "coupon_discount": '',
            "roundoff": '',
            "total_item": 2,
            "paid_amount": 0,
            "due_amount": 0,
            "invoice_no": 'XYZ-1234',
            "invoice_date": formatted_date,
        }  
        session['cart'] = cart
        session['context']= json.dumps(context, default=custom_serializer)
        session.save()

        response = self.client.get(reverse('after_bill_print'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Order created successfully"})

        # Verify that the order was created
        order = Order.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_amount, Decimal("200.00"))  # 2 items * 100 each
        self.assertEqual(order.discount_amount, Decimal("20.00"))  # 10*2 + 50 coupon
        self.assertEqual(order.actual_amount, Decimal("180.00"))  # 200 - 70
        self.assertEqual(order.paid_amount, Decimal("180.00"))  # Paid amount
        self.assertEqual(order.due_amount, Decimal("0.00"))  # Paid in full

        # Verify order item was created
        order_item = OrderItem.objects.filter(order=order).first()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.sku, "TEST123")
        self.assertEqual(order_item.quantity, 2)

        # Verify product stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)  # Originally 10, now 8

