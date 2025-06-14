from django.utils import timezone
import random, uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin ,BaseUserManager
from django.db import models



class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """

    def create_user(self,email,password,**extra_fields):
        """
        Create a regular user with the given email and password.
        """
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model( email=email , **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, email, password):
        """"Validate, Create and store superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    APP_LEVEL_ROLE_CHOICES = (
        ("landlord","Landlord"),
        ("tenant","Tenant"),
        ("admin","Admin")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField( max_length=64, null=True,blank=True)
    last_name = models.CharField( max_length=64, null=True,blank=True)
    is_verify = models.BooleanField(default=False,null=True,blank=True)
    is_staff = models.BooleanField(default=False)
    app_level_role = models.CharField(max_length=12,default='tenant',choices=APP_LEVEL_ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects= UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    

class Property(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True)
    image = models.FileField(upload_to='property', null=True)
    number_of_units = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.address}"
    

# Individual unit within a property
class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=20)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)
    tenant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_tenant': True})

    def __str__(self):
        return f"{self.property.name} - Unit {self.unit_number}"


# Extra profile info for tenants
class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    current_unit = models.OneToOneField(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Tenant Profile"


class RentPayment(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PENDING', 'Pending'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tenant': True})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_for_month = models.CharField(max_length=20)  # E.g., 'June 2025'
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.payment_for_month} - {self.payment_status}"


class TenantReport(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tenant': True})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tenant.first_name} - {self.title} - {self.status}"


# Lease Agreement
class LeaseAgreement(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tenant': True})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    agreement_file = models.FileField(upload_to='agreements/')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('TERMINATED', 'Terminated')], default='ACTIVE')

    def __str__(self):
        return f"Lease for {self.tenant.first_name} [{self.status}]"