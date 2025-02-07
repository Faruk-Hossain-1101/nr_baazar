from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils.timezone import now
from shop.models.customer import Coupon, CustomerCoupon
from django.contrib import messages

def view_coupon(request):
    coupons = Coupon.objects.filter(is_active=True)
    return render(request, 'shop/coupon/index.html', {'coupons': coupons})

def add_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code").strip()
        discount_type = request.POST.get("discount_type")
        discount_amount = request.POST.get("discount_amount")
        max_discount = request.POST.get("max_discount")
        minium_order = request.POST.get("minium_order")
        expiry_date = request.POST.get("expiry_date")
        is_active = 'is_active' in request.POST  # Checkbox checked or not

        # Validate required fields
        if not code or not discount_type or not discount_amount or not expiry_date:
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_coupon')

        # Handle max_discount if not provided (set to 0 if blank)
        if not max_discount:
            max_discount = 0

        # Handle minimum_order if not provided (set to 0 if blank)
        if not minium_order:
            minium_order = 0

        try:
            # Create and save the coupon
            coupon = Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_amount=discount_amount,
                max_discount=max_discount,
                minium_order=minium_order,
                expiry_date=expiry_date,
                is_active=is_active
            )
            messages.success(request, "Coupon added successfully!")
            return redirect('view_coupon')

        except Exception as e:
            messages.error(request, f"An error occurred while adding the coupon: {e}")
            return redirect('add_coupon')

    return render(request, "shop/coupon/add_coupon.html")

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == "POST":
        coupon_code = request.POST.get("code").strip()
        discount_type = request.POST.get("discount_type")
        discount_amount = request.POST.get("discount_amount")
        max_discount = request.POST.get("max_discount")
        minium_order = request.POST.get("minium_order")
        expiry_date = request.POST.get("expiry_date")
        is_active = 'is_active' in request.POST  # Checkbox checked or not

        # Validate required fields
        if not coupon_code or not discount_type or not discount_amount or not expiry_date:
            messages.error(request, "Please fill in all required fields.")
            return redirect('edit_coupon', coupon_id=coupon.id)

        # Handle max_discount if not provided (set to 0 if blank)
        if not max_discount:
            max_discount = 0

        # Handle minimum_order if not provided (set to 0 if blank)
        if not minium_order:
            minium_order = 0

        try:
            # Update the coupon
            coupon.code = coupon_code
            coupon.discount_type = discount_type
            coupon.discount_amount = discount_amount
            coupon.max_discount = max_discount
            coupon.minium_order = minium_order
            coupon.expiry_date = expiry_date
            coupon.is_active = is_active
            coupon.save()

            messages.success(request, "Coupon updated successfully!")
            return redirect('view_coupon')

        except Exception as e:
            messages.error(request, f"An error occurred while updating the coupon: {e}")
            return redirect('edit_coupon', coupon_id=coupon.id)

    return render(request, "shop/coupon/edit_coupon.html", {"coupon": coupon})

def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon", "").strip()
        
        try:
            total_amount = Decimal(request.POST.get("total_amount", "0"))
        except ValueError:
            return JsonResponse({"success": "error", "message": "Invalid total amount"})

        # Validate input
        if not coupon_code or total_amount <= 0:
            return JsonResponse({"success": False, "message": "Invalid input"})

        # Check if the coupon exists and is active
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if not coupon:
            print(coupon)
            return JsonResponse({"success": False, "message": "Invalid or inactive coupon"})

        # Check if the coupon is expired
        if coupon.expiry_date <= now():
            return JsonResponse({"success": False, "message": "Coupon has expired"})
        
        # Check if the order total meets the minimum requirement for the coupon
        if total_amount < coupon.minium_order:
            return JsonResponse({
                "success": False,
                "message": f"Order price should be higher than ₹{coupon.minium_order}"
            })
        
        # Check if the coupon has already been used
        if CustomerCoupon.objects.filter(coupon=coupon, is_used=True).exists():
            return JsonResponse({"success": False, "message": "Coupon already used by"})
        

        # Calculate discount amount
        if coupon.discount_type == "flat":
            discount_amount = min(coupon.discount_amount, total_amount)
        else:  # Percentage discount
            discount_amount = (total_amount * coupon.discount_amount) / Decimal("100")
            if coupon.max_discount:  # Apply max discount limit if set
                discount_amount = min(discount_amount, coupon.max_discount)

        # Calculate final amount after applying the coupon
        final_amount = total_amount - discount_amount

        return JsonResponse({
            "success": True,
            "message": f"₹ {str(discount_amount.quantize(Decimal('0.01')))} Coupon applied!",
            "discount_type": coupon.discount_type,
            "discount_amount": str(discount_amount.quantize(Decimal('0.01'))),
            "final_amount": str(final_amount.quantize(Decimal('0.01')))
        })

    return JsonResponse({"success": False, "message": "Invalid request method"})
