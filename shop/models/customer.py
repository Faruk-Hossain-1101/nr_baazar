from django.db import models
from django.utils.timezone import now

class Customer(models.Model):
    phone = models.CharField(max_length=15)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('percentage', 'Percentage')
    ]
    COUPON_TYPE_CHOICES = [
        ('global', 'Global'),
        ('individual', 'Individual')
    ]

    code = models.CharField(max_length=25, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    minium_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateTimeField()
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default='global')


    def is_valid(self):
        """Check if the coupon is active and not expired"""
        return self.is_active and self.expiry_date > now()


    def __str__(self):
        return f"{self.code} ({'Active' if self.is_valid() else 'Expired'})"
   
    
class CustomerCoupon(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name or 'Unknown'} - {self.coupon.code}"