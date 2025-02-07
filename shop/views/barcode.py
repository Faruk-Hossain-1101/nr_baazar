from django.shortcuts import render
from django.http import JsonResponse
from shop.models.product import Product

def print_labels(p_ids):

    # Fetch the products from the database
    products = Product.objects.filter(id__in=p_ids)

    label_pairs = []  # Store pairs of labels

    remainder = None  # Track the extra label

    for product in products:
        qty = product.stock_quantity

        # Print as many full label pairs as possible
        for _ in range(qty // 2):
            label_pairs.append((product.sku, product.sku))  # Label 1 & 2 same product

        # Handle remainder (odd count)
        if qty % 2 == 1:
            if remainder is None:
                remainder = (product.sku, None)  # Save for next iteration
            else:
                label_pairs.append((remainder[0], product.sku))  # Use previous remainder with this product
                remainder = None  # Reset

    # If an unpaired label remains at the end
    if remainder:
        label_pairs.append((remainder[0], None))
        
    return label_pairs


def show_barcode_data(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'shop/barcode/index.html', {'products': products} )

def preview_barcode(request):
    product_ids = request.GET.get('products', '').split(',')
    # Get product IDs from the query string
    return render(request, 'shop/barcode/barcode_preview.html', {"label_pairs": print_labels(product_ids), "p_ids": product_ids})

def print_barcode(request):
    p_ids = request.GET.get('p_ids').split(", ")
    for id in p_ids:
        Product.objects.filter(id=id).update(is_printed=True)

    return JsonResponse({"success": True, "message":"Printing Completed"})