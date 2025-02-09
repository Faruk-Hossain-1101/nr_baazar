import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils.timezone import now
from shop.models.product import Product
from shop.models.customer import Coupon, Customer, CustomerCoupon
from datetime import datetime, timedelta
from shop.models.order import Order


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

    return JsonResponse({
        'success': True,
        'product_name': product.name,
        'rate': product.actual_price,
        'discount': round(discount, 2),
    })

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
    

def show_invoice(request):
    cart_data = request.session.get("cart", {})
    
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = data.get('cart', {})
        
        # You can store the cart in session if needed
        request.session['cart'] = cart
        
        # Return a JSON response to confirm the cart update
        return JsonResponse({'success': True, 'cart': cart})
    
    # Get the current UTC time and adjust for Kolkata timezone (UTC+5:30)
    current_time_utc = datetime.utcnow()
    kolkata_time = current_time_utc + timedelta(hours=5, minutes=30)


    total_item = 0
    item_discount = Decimal(0)  # Using Decimal for item_discount

    # Calculate total discount (discount * quantity for each item)
    for item in cart_data.get('items', []):
        # Calculate the discount for the current item (discount * qty)
        item_discount += Decimal(item.get('discount', 0)) * int(item.get('qty', 1))
        # Calculate the total quantity of items
        total_item += int(item.get('qty', 1))

    total_discount = item_discount + Decimal(cart_data.get('roundOff', 0))

    # Get total amount after discount
    total_amount = Decimal(cart_data.get("totalAmount", 0))
    paid_amount = Decimal(cart_data.get("paidAmount", 0))
    coupon_discount = Decimal(cart_data.get('coupon', '').get('amount', 0))

    # Calculate grand total after all discounts
    grand_total = total_amount - (total_discount + coupon_discount)
    if paid_amount <= 0:
        due_amount = Decimal(0)
    else:
        due_amount = grand_total - paid_amount

     # Quantize all amounts to two decimal places
    total_discount = total_discount.quantize(Decimal('0.00'))
    grand_total = grand_total.quantize(Decimal('0.00'))
    total_amount = total_amount.quantize(Decimal('0.00'))
    coupon_discount = coupon_discount.quantize(Decimal('0.00'))
    due_amount = due_amount.quantize(Decimal('0.00'))
    paid_amount = paid_amount.quantize(Decimal('0.00'))


    # Generate unique invoice number and formatted date-time
    invoice_number = generate_invoice_number()
    formatted_date = kolkata_time.strftime('%d/%m/%Y')
    
    context = {
        "cart_data": cart_data,
        "total_discount": total_discount,
        "grand_total": grand_total,
        "total_amount": total_amount,
        "coupon_discount": coupon_discount,
        "total_item": total_item,
        "paid_amount": paid_amount,
        "due_amount": due_amount,
        "invoice_no": invoice_number,
        "invoice_date": formatted_date,

    }

    return render(request, "shop/sell/invoice.html", context)
    
