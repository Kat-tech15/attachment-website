from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

#


class Attachee(models.Model):
    #user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    institution = models.CharField(max_length= 255)
    course = models.CharField(max_length=255)
    preferred_start = models.DateField()

    

class Company(models.Model):
    #user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length= 255)
    email  = models.EmailField()
    phone_number = models.CharField(max_length=10)
    location = models.CharField(max_length= 255)

class AttachmentPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=25)
    descrition = models.TextField()
    slots = models.IntegerField()
    start_date = models.DateField()
    post_type = models.CharField(max_length=30, choices=[('attachment', 'Attachment'),('internship','Internship')])
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    attachee = models.ForeignKey(Attachee,on_delete=models.CASCADE)
    post = models.ForeignKey(AttachmentPost, on_delete=models.CASCADE)
    date_applied = models.DateTimeField(auto_now_add=True)



class Tenant(models.Model):
    #user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    location = models.CharField(max_length=255)
    

class RentalListing(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    description = models.TextField()
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    photo =models.ImageField(upload_to='rentals/')
    posted_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    message = models.TextField()