from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField





class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('tenant', 'Tenant')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def has_priviledge(self, allowed_roles):
        return self.role in allowed_roles or self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.username}({self.role})"

class Attachee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 255)
    email = models.EmailField()
    phone_number = PhoneNumberField(region='KE')
    institution = models.CharField(max_length= 255)
    course = models.CharField(max_length=255)
   

    

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length= 255)
    email  = models.EmailField()
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length= 255)

    def __str__(self):
        return self.user.username
    
class AttachmentPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    location = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    slots = models.IntegerField()
    application_link = models.URLField(help_text="Link to the application page.")
    application_deadline = models.DateField(auto_created=True)
    post_type = models.CharField(max_length=30, choices=[('attachment', 'Attachment'),('internship','Internship')])
    created_at = models.DateTimeField(auto_now_add=True)
   

class AttachmentApplication(models.Model):
    attachee = models.ForeignKey(Attachee, on_delete=models.CASCADE, null=True, blank=True)
    attachment_post = models.ForeignKey(AttachmentPost, on_delete=models.CASCADE, null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approaved', 'Approaved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    cv = models.ImageField()
    cover_letter = models.ImageField()
    recommendation = models.ImageField()
    start_date = models.DateField(auto_created=True)
    end_date = models.DateField(auto_created=True)



    class Meta:
        unique_together = ('attachee', 'attachment_post')

    def __str__(self):
        return f"{self.full_name} applied to {self.attachment.company.name}"
    
class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length=255)
    
class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()


class House(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    owner_name  = models.CharField(max_length=200)
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length=200)
    DESCRIPTION_CHOICES =(
        ('single_room', 'Single Room'),
        ('double_room', 'Double Room'),
        ('bed_sitter', 'Bed Sitter'),
        ('hostel', 'Hostel'),
    )
    description = models.CharField(max_length=255, choices=DESCRIPTION_CHOICES, default='single_room')
    total_rooms = models.PositiveIntegerField(default=1)
    rent  = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.IntegerField(default=0)
    image = models.ImageField(upload_to='house_photos/')
    date_posted = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.owner_name

class Room(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.room_number} - {'Booked' if self.is_booked else 'Available'}"

class Booking(models.Model):
    attachee = models.ForeignKey(Attachee, on_delete=models.CASCADE, null=True)
    rental_post = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200)
    phone_number = PhoneNumberField(region='KE')
    created_at = models.DateTimeField(auto_now_add=True)
    move_in_date = models.DateField(auto_now_add=True)
    move_out_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [
        ('cancelled','Cancelled'),
        ('pending', 'Pending'),
        ('approaved', 'Approaved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.full_name} booked {self.rental_post} "



class HouseReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rental = models.ForeignKey('attachment.House', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CompanyReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey('attachment.Company', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Testimonials(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials_photos/', default='default-avatar.jpg')

    def __str__(self):
        return f"{self.name} - {self.role}"


User = get_user_model()

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"To {self.recipient}: {self.message}"