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

    def __str__(self):
        return self.user.username
    
class AttachmentPost(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    email = models.EmailField()
    location = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    slots = models.IntegerField()
    application_deadline = models.DateField(auto_created=True)
    post_type = models.CharField(max_length=30, choices=[('attachment', 'Attachment'),('internship','Internship')])
    created_at = models.DateTimeField(auto_now_add=True)
   

class AttachmentApplication(models.Model):
    attachee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    attachment_post = models.ForeignKey('AttachmentPost', on_delete=models.CASCADE, null=True, blank=True)


    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    cv = models.ImageField()
    cover_letter = models.ImageField()
    recommendation = models.ImageField()
    preferred_start = models.DateField(auto_created=True)


    class Meta:
        unique_together = ('attachee', 'attachment_post')

    def __str__(self):
        return f"{self.full_name} applied to {self.attachment.company.name}"
    
class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
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
    owner_name  = models.CharField(max_length=200)
    contact = models.CharField(max_length=10, null=True)
    location = models.CharField(max_length=200)
    description = models.CharField(max_length=255)
    rent  = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='house_photos/')
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.owner_name

class Booking(models.Model):
    attachee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    rental_post = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200)
    contact = models.CharField(max_length=10, null=True)
    board_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} booked {self.rental_post} "


