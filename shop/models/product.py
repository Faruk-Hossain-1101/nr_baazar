from django.db import models

class Product(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('percentage', 'Percentage')
    ]
    name = models.CharField(max_length=255)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    stock_quantity = models.IntegerField()
    barcode = models.CharField(max_length=25, null=True, blank=True)
    sku = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    cell = models.CharField(max_length=10, null=True, blank=True, default='')
    is_printed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name