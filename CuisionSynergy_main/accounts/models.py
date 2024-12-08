from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for the User model that defines methods for creating users and superusers."""

    def create_user(self, first_name, last_name, username, email, password=None):
        """Create and return a regular user with the first_name,last_name,username,email,password."""
        if not email:
            raise ValueError("User must have an Email Address")
        if not username:
            raise ValueError("User must have Username")

        # Create a new user instance
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        # Hash the user's password
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        """Create and return a superuser with the first_name,last_name,username,email,password."""
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # Assign superuser-specific attributes
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Custom User model that replaces Django's default user model.
    Supports additional fields and role-based functionality."""
    RESTAURANT = 1
    CUSTOMER = 2

    ROLE_CHOICES = (
        (RESTAURANT, 'Restaurant'),  # Role for restaurant users
        (CUSTOMER, 'Customer')  # Role for customer users
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)  # Timestamp for user creation
    last_login = models.DateTimeField(auto_now_add=True)  # Timestamp for last login
    modified_date = models.DateTimeField(auto_now_add=True)  # Last modification timestamp
    created_date = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    is_admin = models.BooleanField(default=False)  # Indicates if user is an admin
    is_staff = models.BooleanField(default=False)  # Indicates if user has staff privileges
    is_active = models.BooleanField(default=False)  # Indicates if user is active
    is_superadmin = models.BooleanField(default=False)  # Indicates if user is a superadmin

    # Associate the custom manager
    objects = UserManager()

    # Authentication-related fields
    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # Fields required when creating a user

    def __str__(self):
        """String representation of the user object."""
        return self.email

    def has_perm(self, perm, obj=None):
        """Determine if the user has a specific permission."""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Determine if the user has permissions for a specific app."""
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='users/profile_pics', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_pics', blank=True, null=True)
    address_1 = models.CharField(max_length=50, blank=True, null=True)
    address_2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
