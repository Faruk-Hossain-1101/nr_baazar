from django.shortcuts import render, redirect, get_object_or_404
from shop.models.product import Product
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import random
from decimal import Decimal
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
        # Get data from the form
        name = request.POST.get('name')
        stock_quantity = request.POST.get('stock_quantity')
        description = request.POST.get('description')
        discount_type = request.POST.get('discount_type')
        color = request.POST.get('color')
        size = request.POST.get('size')
        cell = request.POST.get('cell')
        
        # Initialize error messages
        error_messages = []
        
        # Ensure the input is sanitized before converting to Decimal
        try:
            purchase_price = request.POST.get('purchase_price', '').replace(",", "").strip()
            actual_price = request.POST.get('actual_price', '').replace(",", "").strip()
            selling_price = request.POST.get('selling_price', '').replace(",", "").strip()

            # Only convert if the value is not empty
            if purchase_price:
                purchase_price = Decimal(purchase_price)
            else:
                error_messages.append("Purchase price is required.")

            if actual_price:
                actual_price = Decimal(actual_price)
            else:
                error_messages.append("Actual price is required.")

            if selling_price:
                selling_price = Decimal(selling_price)
            else:
                error_messages.append("Selling price is required.")

        except (ValueError, Decimal.InvalidOperation) as e:
            error_messages.append("Invalid decimal format in price fields.")
        
        discount_amount = request.POST.get('discount_amount', '').replace(",", "").strip()

        try:
            # Convert discount_amount to Decimal, if provided
            if discount_amount:
                discount_amount = Decimal(discount_amount)
            else:
                discount_amount = None  # Optional field
        except (ValueError, Decimal.InvalidOperation) as e:
            discount_amount = None


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
            })

        try:
            sku=generate_sku(name)

            if len(sku) > 10:
                barcode = sku[:10]
            elif len(sku) < 10:
                barcode = sku.ljust(10, '0')
            else:
                barcode = sku

            # Create the product object and save 
            product = Product(
                name=name,
                sku=sku,
                stock_quantity=stock_quantity,
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

            create_label(sku, barcode, size, actual_price, color, cell)

            # Display success message
            messages.success(request, f"{sku}- {stock_quantity} - Product added successfully!")

            # Redirect to the same form with a success message
            return redirect('add_product')

        except IntegrityError:
            error_messages.append("SKU must be unique.")
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
            })

        except ValidationError as e:
            error_messages.append(str(e))
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
            })
    
    else:
        return render(request, 'shop/add_product.html')

def view_product(request):
    if request.method == "GET":
        products = Product.objects.all().order_by('-id')
        return render(request, 'shop/view_product.html', {'products': products})
    
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        # Get the form data from POST request
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        stock_quantity = request.POST.get('stock_quantity')
        purchase_price = request.POST.get('purchase_price')
        actual_price = request.POST.get('actual_price')
        selling_price = request.POST.get('selling_price')
        discount_type = request.POST.get('discount_type')
        discount_amount = request.POST.get('discount_amount')
        description = request.POST.get('description')
        color = request.POST.get('color')
        size = request.POST.get('size')
        cell = request.POST.get('cell')
        barcode = request.POST.get('barcode')

        # Initialize error messages
        error_messages = []

        # Perform necessary validation
        try:
            # You can add custom validation here as per your needs
            if not name or not sku or not stock_quantity or not purchase_price or not actual_price:
                error_messages.append("Required fields are missing!")

            # Update the product
            product.name = name
            product.sku = sku
            product.stock_quantity = stock_quantity
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

            create_label(sku, barcode, size, actual_price, color, cell)
            # Success message
            messages.success(request, f'{sku} - Product updated successfully.')
            return redirect('view_product')  # Redirect to the product list page
        except ValueError as e:
            # Handle form validation errors
            error_messages.append(request, f"Error: {str(e)}")
    else:
        # Render the form with pre-filled product data
        return render(request, 'shop/edit_product.html', {'product': product})