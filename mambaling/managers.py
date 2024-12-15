from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model to handle user creation with email as the unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be provided.'))

        # Normalize the email address by lowercasing the domain part
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Ensure default active status for regular users

        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash and set the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)  # Superuser must be staff
        extra_fields.setdefault('is_superuser', True)  # Superuser must have superuser privileges
        extra_fields.setdefault('is_active', True)  # Ensure the superuser is active
        extra_fields.setdefault('user_type', 'superuser')  # Set default user_type to 'superuser'

        # Validation checks for superuser fields
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
