from django.db import models
from .order import Order
import uuid

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending')
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"