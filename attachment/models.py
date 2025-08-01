from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
import random


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('tenant', 'Tenant')
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
    
    def __str__(self):
        return f"{self.company.name} - {self.post_type} ({self.application_deadline})"

class ApplicationVisit(models.Model):
    attachee = models.ForeignKey('Attachee', on_delete=models.CASCADE)
    attachment_post = models.ForeignKey('AttachmentPost', on_delete=models.CASCADE)
    visited_at = models.DateTimeField(default=timezone.now)


    class Meta:
        unique_together = ('attachee', 'attachment_post')

    def __str__(self):
        return f"{self.full_name} visited {self.attachment.company.name}"
    
class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(region='KE')
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
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
    image = models.ImageField(upload_to='house_photos/')
    date_posted = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.owner_name

class Room(models.Model):
    ROOM_TYPE_CHOICES = ( 
        ('single_room', 'Single Room'),
        ('double_room', 'Double Room'),
        ('bed_sitter', 'Bed Sitter'),
        ('hostel', 'Hostel'),
    )

    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, default='single_room')
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    is_booked = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.room_number} - {'Booked' if self.is_booked else 'Available'}"

class Booking(models.Model):
    attachee = models.ForeignKey(Attachee, on_delete=models.CASCADE, null=True)
    house_post = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    phone_number = PhoneNumberField(region='KE')
    created_at = models.DateTimeField(auto_now_add=True)
    move_in_date = models.DateField(null=True,blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [
        ('cancelled','Cancelled'),
        ('pending', 'Pending'),
        ('approaved', 'Approaved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.full_name} booked {self.house_post} "



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
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='notifications'
        )
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"To {self.recipient}: {self.message}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField()
    is_registered_user = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_identity = self.user.username if self.user else (self.name or "Anonymus")
        return f"Feeback by {user_identity} on {self.submitted_at.strftime('%Y-%m-%d')}"
    
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)