from typing import Any
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin,User
from CompanyManagement.models import Company

# Creating Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, name, role, company, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not role:
            raise ValueError('User must have a role')
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role,
            company=company
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name,role, company, password=None):
        user = self.create_user(
            email=email,
            name=name,
            role=role,
            company=company,
            password=password
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Creating Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    ROLES_CHOICES = (
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee')
    )
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=ROLES_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()  
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role', 'company']  
    
    def __str__(self):
        return self.email
