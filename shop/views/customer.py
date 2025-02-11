from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from shop.models.customer import Customer  


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
    return render(request, 'shop/customer/customer_detail.html', {'customer': customer})
