from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Creates and returns a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Default active status
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Creates and returns a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)
