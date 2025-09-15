from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Attachee, Company, Tenant, Booking, House, Notification, Announcement

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check user type and create appropriate profile
        if instance.role == 'attachee':
            Attachee.objects.create(user=instance)
            print("Attachee profile created for:", instance.username)
        elif instance.role == 'company':
            Company.objects.create(user=instance)
            print("Company profile created for:", instance.username)
        elif instance.role == 'tenant':
            Tenant.objects.create(user=instance)
            print("Tenant profile created for:", instance.username)

