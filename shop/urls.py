
from django.urls import path
from shop.views import dashboard, product, barcode

urlpatterns = [
    path('', dashboard.index, name='home'),
    path('add-product', product.add_product, name="add_product"),
    path('view-product', product.view_product, name="view_product"),
    path('edit-product/<int:id>/', product.edit_product, name="edit_product"),
    path('print-barcode/', barcode.print_barcode, name="print_barcode"),
]