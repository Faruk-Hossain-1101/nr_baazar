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

    def save(self, *args, **kwargs):
        # If the password is provided in plain text, hash it.
        # Django’s default hashed passwords usually start with "pbkdf2_" (or your chosen algorithm’s prefix).
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
