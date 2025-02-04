from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.managers import CustomUserManager

class CustomUser(AbstractUser):  
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='staff')

    # Ensure these fields exist
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
