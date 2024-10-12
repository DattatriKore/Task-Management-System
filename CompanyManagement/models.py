from django.db import models
from UserAuth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Company(models.Model):
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    contact_no=PhoneNumberField()
    email=models.EmailField()
    
    def __str__(self):
        return self.name