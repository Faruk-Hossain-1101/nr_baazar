
from django.urls import path
from shop.views import dashboard, product

urlpatterns = [
    path('', dashboard.index, name='home'),
    path('add-product', product.add_product, name="add_product"),
    path('view-product', product.view_product, name="view_product"),
]