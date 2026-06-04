from django.db import models
from accounts.models import Landlord, Attachee
from phonenumber_field.modelfields import PhoneNumberField




class House(models.Model):
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, null=True, blank=True)
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