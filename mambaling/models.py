from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser to handle user creation using email instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'superuser')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractUser):
#     username = None
#     email = models.EmailField(_('email address'), unique=True)
#     is_active = models.BooleanField(default=True)
#     is_approved = models.BooleanField(default=False)
    
#     USER_TYPE_CHOICES = [
#         ('superuser', 'Superuser'),
#         ('admin', 'Admin'),
#         ('user', 'User'),
#     ]
#     user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.email

#     groups = models.ManyToManyField(
#         Group,
#         verbose_name=_('groups'),
#         blank=True,
#         help_text=_(
#             'The groups this user belongs to. A user will get all permissions '
#             'granted to each of their groups.'
#         ),
#         related_name="customuser_set",
#         related_query_name="user",
#     )
#     user_permissions = models.ManyToManyField(
#         Permission,
#         verbose_name=_('user permissions'),
#         blank=True,
#         help_text=_('Specific permissions for this user.'),
#         related_name="customuser_set",
#         related_query_name="user",
#     )


class CustomUser(AbstractUser):
    """
    Custom user model that uses email as the unique identifier instead of a username.
    """
    username = None  # Remove the username field
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

    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = []  # No additional fields required when creating a user

    objects = CustomUserManager()  # Use the custom user manager

    # Optional: Override string representation for better display
    def __str__(self):
        return self.email

    # Permissions and groups handling
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )

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
