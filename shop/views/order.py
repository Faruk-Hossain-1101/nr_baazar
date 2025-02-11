from django.shortcuts import render
from shop.models.order import Order, OrderItem

def orders_view(request):
    orders = Order.objects.all().order_by("-id")  # Fetch all orders
    return render(request, 'shop/order/orders_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'shop/order/order_detail.html', {'order': order, 'order_items': order_items})
