
from django.urls import path
from shop.views import dashboard, product, barcode, sell, customer, coupon, order

urlpatterns = [
    path('', dashboard.index, name='home'),
    path('add-product', product.add_product, name="add_product"),
    path('view-product', product.view_product, name="view_product"),
    path('edit-product/<int:id>/', product.edit_product, name="edit_product"),

    #Barcode
    path('show-barcode-data/', barcode.show_barcode_data, name="show_barcode_data"),
    path('preview-barcode/', barcode.preview_barcode, name="preview_barcode"),
    path('print-barcode/', barcode.print_barcode, name="print_barcode"),

    # Sell product
    path('sell/', sell.index, name="sell"),
    path('get-product/', sell.get_product_details, name='get_product_details'),
    path('check-discount/', sell.check_discount, name='check_discount'),
    path('check-qty/', sell.check_qty, name='check_qty'),
    path('show-invoice/', sell.show_invoice, name='show_invoice'),
    path('after-bill-print/', sell.after_bill_print, name='after_bill_print'),

    # Coupon
    path('apply-coupon/', coupon.apply_coupon, name='apply_coupon'),
    path('add-coupon/', coupon.add_coupon, name='add_coupon'),
    path('view-coupon/', coupon.view_coupon, name='view_coupon'),
    path('edit-coupon/<int:coupon_id>/', coupon.edit_coupon, name='edit_coupon'),

    # Customer
    path('customers/', customer.customers_list, name='customers_list'),
    path('customers/<int:customer_id>/', customer.customer_detail, name='customer_detail'),
    path('get-customer-by-phone/', customer.get_customer_by_phone, name="get_customer_by_phone"),

    # Orders
    path('orders/', order.orders_view, name='orders_list'),
    path('orders/<int:order_id>/', order.order_detail, name='order_detail'),
]