import json
import uuid
from decimal import Decimal
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models.product import Product
from shop.models.customer import Coupon, Customer, CustomerCoupon
from shop.models.order import Order, OrderItem
from shop.models.payment import Payment
from django.db import transaction
from django.db.models import F


# Function to convert non-serializable types
def custom_serializer(obj):
    if isinstance(obj, Decimal):  # Convert Decimal to float
        return float(obj)
    if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime):  # Convert datetime to string
        return obj.strftime("%Y-%m-%d")
    raise TypeError(f"Type {type(obj)} not serializable")


def generate_invoice_number():
    # Generate a unique invoice number using UUID
    no = f"NRB-{uuid.uuid4().hex.upper()[:8]}"
    if Order.objects.filter(order_number=no):
        return generate_invoice_number()

    return no

def index(request):
    return render(request, 'shop/sell/index.html')

def get_product_details(request):
    barcode = request.GET.get('barcode', '')

    if len(barcode) != 10:
        return JsonResponse({'success': False, 'message': 'Invalid barcode length'})

    product = get_object_or_404(Product, barcode=barcode)

    # Calculate discount based on type
    if product.discount_type == 'flat':
        discount = product.discount_amount
    elif product.discount_type == 'percentage':
        discount = (product.discount_amount / 100) * product.actual_price
    else:
        discount = 0  # Default to no discount if type is invalid

    context = {
        'success': True,
        'product_name': product.name,
        'rate': product.actual_price,
        'discount': round(discount, 2),
        'color': product.color,
        'size': product.size,
        'sku':product.sku
    }
    return JsonResponse(context)

def check_discount(request):
    discount_amount = request.GET.get('discount_amount', '')
    barcode = request.GET.get('barcode', '')

    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})

    actual_price = product.actual_price  # Selling price before discount (Decimal)
    purchase_price = product.purchase_price  # Purchase price (Decimal)

    try:
        discount_amount = Decimal(discount_amount)  # Convert to Decimal
    except:
        return JsonResponse({'success': False, 'message': 'Invalid discount amount'})

    # Calculate discounted selling price
    discounted_price = actual_price - discount_amount

    # Ensure at least a 5% margin
    min_selling_price = purchase_price * Decimal("1.05")  # Keep Decimal precision

    if discounted_price >= min_selling_price:
        return JsonResponse({'success': True, 'message': 'Valid discount'})
    else:
        return JsonResponse({'success': False, 'message': 'Discount too high! Minimum 5% margin required.'})

def check_qty(request):
    qty = request.GET.get('qty', '')
    barcode = request.GET.get('barcode', '')

    try:
        product = Product.objects.get(barcode=barcode)
        if product.stock_quantity >= int(qty):
            return JsonResponse({'success': True, 'message': 'Product available!'})
        
        return JsonResponse({'success': False, 'message': 'Quantity higher than stock availability!'})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})
    
@transaction.atomic
def show_invoice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = data.get('cart', {})
        
        # You can store the cart in session if needed
        request.session['cart'] = cart
        
        # Return a JSON response to confirm the cart update
        return JsonResponse({'success': True, 'cart': cart})
    
    if request.method == "GET":
        cart_data = request.session.get("cart", {})
        coupon_data = cart_data.get("coupon", {})
        
        # Get the current UTC time and adjust for Kolkata timezone (UTC+5:30)
        current_time_utc = datetime.utcnow()
        kolkata_time = current_time_utc + timedelta(hours=5, minutes=30)


        total_item = 0
        item_discount = Decimal(0)  # Using Decimal for item_discount
        actual_price = Decimal(0)
        # Calculate total discount (discount * quantity for each item)
        for item in cart_data.get('items', []):
            actual_price += Decimal(item.get('rate', 0)) * int(item.get('qty', 1))
            # Calculate the discount for the current item (discount * qty)
            item_discount += Decimal(item.get('discount', 0)) * int(item.get('qty', 1))
            total_item += int(item.get('qty', 1))

        # Get total amount after discount
        total_amount = actual_price - item_discount
        paid_amount = Decimal(cart_data.get("paidAmount", 0))
        coupon_discount = Decimal(coupon_data.get('amount', 0))
        roundoff = Decimal(cart_data.get('roundOff', 0))

        # Calculate grand total after all discounts
        grand_total = total_amount - (coupon_discount+roundoff)
        if paid_amount <= 0:
            due_amount = Decimal(0)
        else:
            due_amount = grand_total - paid_amount

        # Quantize all amounts to two decimal places
        actual_price = actual_price.quantize(Decimal('0.00'))
        item_discount = item_discount.quantize(Decimal('0.00'))
        total_amount = total_amount.quantize(Decimal('0.00'))
        grand_total = grand_total.quantize(Decimal('0.00'))
        coupon_discount = coupon_discount.quantize(Decimal('0.00'))
        roundoff = roundoff.quantize(Decimal('0.00'))
        due_amount = due_amount.quantize(Decimal('0.00'))
        paid_amount = paid_amount.quantize(Decimal('0.00'))


        # Generate unique invoice number and formatted date-time
        invoice_number = generate_invoice_number()
        formatted_date = kolkata_time.strftime('%d/%m/%Y')

        context = {
            "cart_data": cart_data,
            'actual_price': actual_price,
            "item_discount": item_discount,
            "total_amount": total_amount,
            "grand_total": grand_total,
            "coupon_discount": coupon_discount,
            "roundoff": roundoff,
            "total_item": total_item,
            "paid_amount": paid_amount,
            "due_amount": due_amount,
            "invoice_no": invoice_number,
            "invoice_date": formatted_date,
        }  
        request.session['context'] = json.dumps(context, default=custom_serializer)
        return render(request, "shop/sell/invoice.html", context)

def after_bill_print(request): 
    if request.method == "GET":
        cart_data = request.session.get("cart", {})
        customer_data = cart_data.get("customer", {})
        coupon_data = cart_data.get("coupon", {})
        context = json.loads(request.session.get('context', '{}'))

        # Now create the customer, order, and order items
        customer, created = Customer.objects.get_or_create(
            phone=customer_data.get('phone', ''),
            defaults={'name': customer_data.get('name', ''), 'address': customer_data.get('address', '')}
        )

        # Found Coupon
        coupon = None
        if coupon_data:
            coupon = Coupon.objects.filter(code=coupon_data.get('code')).first()

            if coupon.coupon_type == 'individual':
                CustomerCoupon.objects.filter(customer=customer).update(is_used = True)


        # Create the order
        order = Order.objects.create(
            order_number=context['invoice_no'],
            customer=customer,
            total_amount=context['actual_price'],
            discount_amount=context['roundoff']+context['coupon_discount']+context['item_discount'],
            actual_amount=context['grand_total'],
            coupon=coupon,
        )

        # Create order items
        for item in cart_data.get('items', []):
            qty = int(item.get('qty', 1))
            Product.objects.filter(sku=item.get('sku', '')).update(stock_quantity=F('stock_quantity') - qty)

            OrderItem.objects.create(
                order=order,
                product_name=item.get('productName', ''),
                actual_price=Decimal(item.get('rate', 0)),
                discount_amount=Decimal(item.get('discount', 0)),
                color=item.get('color', ''),
                size=item.get('size', ''),
                quantity=qty,
                sku=item.get('sku', ''),
            )
        
        paid_amount=context['paid_amount'] if context['paid_amount'] > 0 else context['grand_total']
        due_amount=context['due_amount']
        payment_type=cart_data.get('paymentType', 'cash')  # Adjust if using a different payment type
        payment_status='success'  # You can change this if needed
        
        Payment.objects.create(
            order=order,
            payment_method=payment_type,
            payment_status=payment_status,
            paid_amount=paid_amount,
            due_amount=due_amount if due_amount > 0 else None,
        )
        
           
        request.session['cart'] = None
        request.session['context'] = None
        
        return JsonResponse({"success": True, "message": "Order created successfully"})
