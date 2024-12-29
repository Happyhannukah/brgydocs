from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .managers import CustomUserManager 
import datetime


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


class CustomUser(AbstractUser):
    """
    Custom user model that uses email as the unique identifier instead of a username.
    """
    username = None  # Remove the default username field
    email = models.EmailField(_('email address'), unique=True)  # Use email as the unique identifier
    is_active = models.BooleanField(default=True)  # Indicates if the account is active
    is_approved = models.BooleanField(default=False)  # Custom field for admin/superuser approval

    USER_TYPE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        help_text=_('Defines the role of the user in the system.')
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text=_("Optional profile picture.")
    )

    USERNAME_FIELD = 'email'  # Use email as the unique username field
    REQUIRED_FIELDS = []  # No additional fields are required when creating a user

    objects = CustomUserManager()  # Use your custom user manager

    def __str__(self):
        """
        String representation of the user, showing the email.
        """
        return self.email

    # Override the default related names for groups and permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_users",  # Changed related name to avoid conflict
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_users",  # Changed related name to avoid conflict
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class Mambaling(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mambaling_profile",
        primary_key=True
    )
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    
class ProofOfResidency(models.Model):
    file = models.FileField(upload_to='proof_of_residency/')
    clearance_request = models.ForeignKey('ClearanceRequest', related_name='proof_files', on_delete=models.CASCADE)



class ClearanceRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    birthplace = models.CharField(max_length=255)
    birthdate = models.DateField()
    civil_status = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    block_number = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    purpose = models.CharField(max_length=100, blank=True, null=True)  # For Indigency
    residency_duration = models.CharField(max_length=100, blank=True, null=True)  # For Residency
    document_type = models.CharField(max_length=50, choices=[
        ('Barangay Clearance', 'Barangay Clearance'),
        ('Certificate of Indigency', 'Certificate of Indigency'),
        ('Certificate of Residency', 'Certificate of Residency'),
    ])
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    proof_of_residency = models.FileField(upload_to='proof_of_residency/')
    profile_photo = models.ImageField(upload_to='profile_photos/')
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    ], default='Pending')
    decline_reason = models.TextField(blank=True, null=True)
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.document_type} - {self.status}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.message[:50]}..."
