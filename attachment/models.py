from django.db import models

# Create your models here.
class AttacheeInfo(models.Model):
    full_name = models.CharField(max_length= 255)
    phone_number = models.IntegerField()
    gender = models.CharField(max_length=10)
    institution = models.CharField(max_length= 255)
    course = models.CharField(max_length=255)
    place_attached = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits= 10, decimal_places= 2)

    def __str__(self):
        return self.full_name

class AttacheeFirmInfo(models.Model):
    name = models.CharField(max_length= 255)
    email  = models.EmailField(max_length= 55)
    phone_number = models.CharField(max_length= 10)
    location = models.CharField(max_length= 255)
    specialization  = models.CharField(max_length =255)
    slots = models.IntegerField()

class ContactInfo(models.Model):
    full_name = models.CharField(max_length= 255)
    email = models.EmailField(max_length=255)
    message = models.TextField()

class TenantsInfo(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    location = models.CharField(max_length=255)
    rent_cost = models.DecimalField(max_digits= 10, decimal_places= 2)
    house_description = models.CharField(max_length=255)

class AttachmentApplication(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    institution = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    cover_letter =models.FileField(upload_to='cover_letters/')
    cv = models.FileField(upload_to='cvs/')
    recommedation_letter = models.FileField(upload_to='recommedations/')

    def __str__(self):
        return self.full_name