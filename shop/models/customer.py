from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('percentage', 'Percentage')
    ]
    code = models.CharField(max_length=25, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code
    
class CustomerCoupon(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.coupon.code}"