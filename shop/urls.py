
from django.urls import path
from shop.views import dashboard, product, barcode, sell, customer

urlpatterns = [
    path('', dashboard.index, name='home'),
    path('add-product', product.add_product, name="add_product"),
    path('view-product', product.view_product, name="view_product"),
    path('edit-product/<int:id>/', product.edit_product, name="edit_product"),
    path('print-barcode/', barcode.print_barcode, name="print_barcode"),

    # Sell product
    path('sell/', sell.index, name="sell"),
    path('get-product/', sell.get_product_details, name='get_product_details'),
    path('check-discount/', sell.check_discount, name='check_discount'),

    # Customer
    path('get-customer-by-phone/', customer.get_customer_by_phone, name="get_customer_by_phone")
]