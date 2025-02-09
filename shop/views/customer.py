from django.http import JsonResponse
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
