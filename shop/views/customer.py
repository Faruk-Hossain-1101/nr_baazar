from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from shop.models.customer import Customer  
from django.db.models import Sum


def get_customer_by_phone(request):
    phone = request.GET.get('phone')
    try:
        customer = Customer.objects.get(phone=phone)
        return JsonResponse({
            'success': True,
            'name': customer.name,
            'address': customer.address
        })
    except Customer.DoesNotExist:
        return JsonResponse({'success': False}) 
    
def customers_list(request):
    # Fetch all customers from the database
    customers = Customer.objects.all()
    # Render the customers list template with the customers data
    return render(request, 'shop/customer/customers_list.html', {'customers': customers})

def customer_detail(request, customer_id):
    # Get the customer and their orders
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.order_set.select_related("payment").all().order_by("-id")

    # Aggregate total spent and total discount
    totals = orders.aggregate(
        total_spent=Sum('actual_amount', default=0),
        total_discount=Sum('discount_amount', default=0)
    )

    context = {
        "customer": customer,
        "orders": orders,
        "total_spent": totals["total_spent"] or 0,
        "total_discount": totals["total_discount"] or 0,
    }
    return render(request, 'shop/customer/customer_detail.html', context)
