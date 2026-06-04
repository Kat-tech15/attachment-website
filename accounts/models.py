from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
import random


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('landlord', 'Landlord')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False, )
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_last_sent = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_privilege(self, allowed_roles):
        return self.role in allowed_roles or self.is_superuser or self.is_staff

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_created_at = timezone.now()
        self.otp_last_sent = timezone.now()
        self.save()
        return self.otp
    
    def is_otp_expired(self):
        if self.otp_created_at is None:
            return True
        expiration_time = self.otp_created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time

    def can_resend_otp(self):
        if self.otp_last_sent is None:
            return True
        next_allowed_time = self.otp_last_sent + timedelta(minutes=1)

class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()

class Attachee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 255)
    email = models.EmailField()
    phone_number = PhoneNumberField(region='KE')
    institution = models.CharField(max_length= 255)
    course = models.CharField(max_length=255)
   
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length= 255)
    email  = models.EmailField()
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length= 255)

    def __str__(self):
        return self.user.username
    
class Landlord(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username