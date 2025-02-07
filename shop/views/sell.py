from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils.timezone import now
from shop.models.product import Product
from shop.models.customer import Coupon, Customer, CustomerCoupon


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
