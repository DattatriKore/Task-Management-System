from django.db import models
from CompanyManagement.models import Company
from datetime import date
from UserAuth.models import User
from django.utils import timezone

# Create your models here.
# Task Category
class Category(models.Model):
    name=models.CharField(max_length=100)

# Task   
class Task(models.Model):
    PRIORITY_CHOICE=[
        ('Low', 'Low'), 
        ('Medium', 'Medium'), 
        ('High', 'High')
    ]
    title=models.CharField(max_length=100)
    description=models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True, blank=True)
    priority=models.CharField(max_length=100,choices=PRIORITY_CHOICE)
    company=models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

# Task Assign
class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE,null=True,blank=True)
    company=models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date=models.DateField(null=True,blank=True)
    end_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=100,choices=STATUS_CHOICES,default='pending')
