from django.shortcuts import render, redirect, get_object_or_404
from shop.models.product import Product
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import random
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from shop.utils.barcode import create_label

def generate_sku(product_name):
    # Create SKU prefix by taking the first letter of each word in the product name
    name_parts = product_name.split()
    sku_prefix = ''.join([part[0].upper() for part in name_parts])
    
    # Generate a unique number for the SKU
    unique_number = random.randint(10, 999)  # You can customize the range as per your requirement
    
    # Combine the prefix with the unique number
    sku = f"{sku_prefix}{unique_number}"

    # Ensure that the SKU is unique
    while Product.objects.filter(sku=sku).exists():
        unique_number = random.randint(10, 999)
        sku = f"{sku_prefix}{unique_number}"

    return sku

def add_product(request):
    if request.method == 'POST':
        # Retrieve and sanitize input data
        name = request.POST.get('name', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '').strip()
        description = request.POST.get('description', '').strip()
        discount_type = request.POST.get('discount_type', '').strip()
        color = request.POST.get('color', '').strip()
        size = request.POST.get('size', '').strip()
        cell = request.POST.get('cell', '').strip()

        # Initialize error messages
        error_messages = []

        # Validate required fields
        if not name:
            error_messages.append("Product name is required.")
        if not stock_quantity or not stock_quantity.isdigit():
            error_messages.append("Stock quantity must be a valid number.")

        # Handle price fields safely
        try:
            purchase_price = request.POST.get('purchase_price', '').replace(",", "").strip()
            actual_price = request.POST.get('actual_price', '').replace(",", "").strip()
            selling_price = request.POST.get('selling_price', '').replace(",", "").strip()

            purchase_price = Decimal(purchase_price) if purchase_price else None
            actual_price = Decimal(actual_price) if actual_price else None
            selling_price = Decimal(selling_price) if selling_price else None

            if purchase_price is None:
                error_messages.append("Purchase price is required.")
            if actual_price is None:
                error_messages.append("Actual price is required.")
            if selling_price is None:
                error_messages.append("Selling price is required.")
        
        except (ValueError, InvalidOperation):
            error_messages.append("Invalid decimal format in price fields.")

        # Handle discount amount
        try:
            discount_amount = request.POST.get('discount_amount', '').replace(",", "").strip()
            discount_amount = Decimal(discount_amount) if discount_amount else None
        except (ValueError, InvalidOperation):
            discount_amount = None

        # If errors exist, re-render form with previous values
        if error_messages:
            return render(request, 'shop/add_product.html', {
                'error_messages': error_messages,
                'name': name,
                'stock_quantity': stock_quantity,
                'description': description,
                'discount_type': discount_type,
                'purchase_price': purchase_price,
                'actual_price': actual_price,
                'selling_price': selling_price,
                'discount_amount': discount_amount,
                'color': color,
                'size': size,
                'cell': cell,
            })

        try:
            # Generate a unique SKU
            sku = generate_sku(name)

            # Ensure barcode is 10 characters long
            barcode = sku[:10] if len(sku) > 10 else sku.ljust(10, '0')

            # Create and save the product
            product = Product(
                name=name,
                sku=sku,
                stock_quantity=int(stock_quantity),
                purchase_price=purchase_price,
                actual_price=actual_price,
                discount_type=discount_type,
                discount_amount=discount_amount,
                description=description,
                selling_price=selling_price,
                barcode=barcode,
                color=color,
                size=size,
                cell=cell
            )
            product.save()

            # Generate barcode label
            create_label(sku, barcode, size, actual_price, color, cell)

            # Success message
            messages.success(request, f"{sku} - {stock_quantity} units added successfully!")
            return redirect('add_product')

        except IntegrityError:
            messages.error(request, "SKU must be unique.")

    return render(request, 'shop/add_product.html')

def view_product(request):
    if request.method == "GET":
        products = Product.objects.all().order_by('-id')
        return render(request, 'shop/view_product.html', {'products': products})
    
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '').strip()
        purchase_price = request.POST.get('purchase_price', '').replace(",", "").strip()
        actual_price = request.POST.get('actual_price', '').replace(",", "").strip()
        selling_price = request.POST.get('selling_price', '').replace(",", "").strip()
        discount_type = request.POST.get('discount_type', '').strip()
        discount_amount = request.POST.get('discount_amount', '').replace(",", "").strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '').strip()
        size = request.POST.get('size', '').strip()
        cell = request.POST.get('cell', '').strip()
        barcode = request.POST.get('barcode', '').strip()

        # Initialize error messages
        error_messages = []

        # Check required fields
        if not name:
            error_messages.append("Product name is required.")
        if not sku:
            error_messages.append("SKU is required.")
        if not stock_quantity.isdigit():
            error_messages.append("Stock quantity must be a valid number.")
        if not purchase_price:
            error_messages.append("Purchase price is required.")
        if not actual_price:
            error_messages.append("Actual price is required.")
        if not selling_price:
            error_messages.append("Selling price is required.")

        # Convert values to Decimal safely
        try:
            purchase_price = Decimal(purchase_price) if purchase_price else None
            actual_price = Decimal(actual_price) if actual_price else None
            selling_price = Decimal(selling_price) if selling_price else None
            discount_amount = Decimal(discount_amount) if discount_amount else None
        except (ValueError, InvalidOperation):
            error_messages.append("Invalid format for price fields.")

        if error_messages:
            return render(request, 'shop/edit_product.html', {
                'product': product,  # Pass the existing product
                'error_messages': error_messages,
                'name': name,
                'sku': sku,
                'stock_quantity': stock_quantity,
                'description': description,
                'discount_type': discount_type,
                'purchase_price': purchase_price,
                'actual_price': actual_price,
                'selling_price': selling_price,
                'discount_amount': discount_amount,
                'color': color,
                'size': size,
                'cell': cell,
                'barcode': barcode,
            })

        try:
            # Update product
            product.name = name
            product.sku = sku
            product.stock_quantity = int(stock_quantity)  # Convert stock to integer
            product.purchase_price = purchase_price
            product.actual_price = actual_price
            product.selling_price = selling_price
            product.discount_type = discount_type
            product.discount_amount = discount_amount
            product.description = description
            product.color = color
            product.size = size
            product.cell = cell
            product.barcode = barcode
            product.save()

            # Generate a new barcode label
            create_label(sku, barcode, size, actual_price, color, cell)

            # Success message
            messages.success(request, f'{sku} - Product updated successfully.')
            return redirect('view_product')

        except IntegrityError:
            messages.error(request, "SKU must be unique.")

    # Render the form with existing product data
    return render(request, 'shop/edit_product.html', {'product': product})