from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models




class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('tenant', 'Tenant'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='attachee')

    def __str__(self):
        return f"{self.username}({self.role})"

class Attachee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    institution = models.CharField(max_length= 255)
    course = models.CharField(max_length=255)
   

    

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length= 255)
    email  = models.EmailField()
    phone_number = models.CharField(max_length=10)
    location = models.CharField(max_length= 255)

class AttachmentPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=25)
    description = models.TextField()
    slots = models.IntegerField()
    application_deadline = models.DateField()
    post_type = models.CharField(max_length=30, choices=[('attachment', 'Attachment'),('internship','Internship')])
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()

class AttachmentApplication(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    cv = models.ImageField()
    cover_letter = models.ImageField()
    recommendation = models.ImageField()
    preferred_start = models.DateField()




class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
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


class House(models.Model):
    name  = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    rent  = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='house_photos/')
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Booking(models.Model):
    tenant =models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

