from django.shortcuts import render
from shop.models.order import Order, OrderItem
from shop.models.payment import Payment

def orders_view(request):
    orders = Order.objects.all().order_by("-id")  # Fetch all orders

    # Add the most recent payment details for each order
    for order in orders:
        payment = Payment.objects.filter(order=order).last()
        order.latest_payment = payment  # Attach the payment object to the order

    return render(request, 'shop/order/orders_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    payment = Payment.objects.filter(order=order).last()  # Get the most recent payment
    return render(request, 'shop/order/order_detail.html', {'order': order, 'order_items': order_items, 'payment': payment})